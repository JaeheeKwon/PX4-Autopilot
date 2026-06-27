# PX4 Flight Controller Threading

PX4 applications run on top of the platform scheduler, usually NuttX on flight
controllers and POSIX threads on simulation or Linux targets. PX4 modules use
two common execution models:

- a dedicated PX4 task/thread created with `px4_task_spawn_cmd()`
- a PX4 work item running on a shared work queue thread

The right model depends on whether the module needs its own blocking loop or can
run as short, bounded callbacks.

## Startup Path

Most modules are started by shell command or by the startup scripts:

```text
<module> start
  -> <module>_main()
     -> ModuleBase::main()
        -> ModuleBase::start_command()
           -> module-specific task_spawn()
```

`ModuleBase` only dispatches the command. The module-specific `task_spawn()`
chooses whether to create a dedicated thread or attach a work item to a shared
queue.

Relevant code:

- `platforms/common/module_base.cpp`
- `platforms/common/include/px4_platform_common/module.h`

## Dedicated Thread Approach

A dedicated-thread module creates an OS scheduling context with
`px4_task_spawn_cmd()`. The new task has its own stack, priority, and main loop.

This is the normal choice when the module:

- blocks in `px4_poll()`, file I/O, serial I/O, or another wait API
- has long or variable-latency work
- owns an event loop that should not delay unrelated modules
- needs an independently tuned stack size or priority

Typical structure:

```cpp
class MyModule : public ModuleBase
{
public:
    static int task_spawn(int argc, char *argv[]);
    static int run_trampoline(int argc, char *argv[]);

    void run() override;
};

int MyModule::task_spawn(int argc, char *argv[])
{
    desc.task_id = px4_task_spawn_cmd("my_module",
                                      SCHED_DEFAULT,
                                      SCHED_PRIORITY_DEFAULT,
                                      1200,
                                      (px4_main_t)&run_trampoline,
                                      (char *const *)argv);

    return desc.task_id < 0 ? -errno : 0;
}

int MyModule::run_trampoline(int argc, char *argv[])
{
    return ModuleBase::run_trampoline_impl(desc,
        [](int ac, char *av[]) -> ModuleBase * {
            return new MyModule();
        },
        argc, argv);
}

void MyModule::run()
{
    while (!should_exit()) {
        // Blocking or polling is acceptable here because this is
        // this module's own thread.
        px4_usleep(10_ms);
    }
}
```

In this model the thread stack exists for the lifetime of the task. Local
variables in one loop iteration still disappear when that iteration's stack
frame exits, so persistent module state still belongs in member variables.

Examples:

- `src/templates/template_module/template_module.cpp`
- `src/modules/navigator/navigator_main.cpp`
- `src/modules/commander/Commander.cpp`

## Work Queue Approach

A work-queue module does not create a private thread for itself. It derives from
`px4::WorkItem` or `px4::ScheduledWorkItem` and attaches to a named PX4 work
queue. Each work queue is backed by one OS thread, and many modules can share
that thread.

Simple layout:

```text
wq:manager
  |
  | creates queue threads lazily
  v
wq:rate_ctrl thread
  |
  | runnable queue: [mc_rate_control] [control_allocator] [...]
  v
pop one WorkItem -> call Run() -> return -> pop next WorkItem
```

The work queue manager starts as `wq:manager`. When a `WorkItem` asks for a
queue such as `wq:rate_ctrl`, `wq:nav_and_controllers`, `wq:hp_default`, or
`wq:lp_default`, PX4 finds the existing queue or creates it.

Relevant code:

- `platforms/common/px4_work_queue/WorkQueueManager.cpp`
- `platforms/common/px4_work_queue/WorkQueue.cpp`
- `platforms/common/px4_work_queue/WorkItem.cpp`
- `platforms/common/px4_work_queue/ScheduledWorkItem.cpp`
- `platforms/common/include/px4_platform_common/px4_work_queue/WorkQueueManager.hpp`

Typical structure:

```cpp
class MyWorkItem : public ModuleBase, public px4::ScheduledWorkItem
{
public:
    MyWorkItem() :
        ScheduledWorkItem("my_work_item", px4::wq_configurations::hp_default)
    {
        // Initialize persistent members only.
    }

    bool init()
    {
        // Register callbacks or schedule first execution here.
        ScheduleOnInterval(10_ms);
        return true;
    }

    static int task_spawn(int argc, char *argv[])
    {
        MyWorkItem *instance = new MyWorkItem();

        if (instance) {
            desc.object.store(instance);
            desc.task_id = task_id_is_work_queue;

            if (instance->init()) {
                return PX4_OK;
            }
        }

        delete instance;
        desc.object.store(nullptr);
        desc.task_id = -1;
        return PX4_ERROR;
    }

private:
    void Run() override
    {
        if (should_exit()) {
            ScheduleClear();
            exit_and_cleanup(desc);
            return;
        }

        // Do one bounded unit of work and return.
    }
};
```

`init()` is not a virtual function supplied by `WorkItem` or `ModuleBase`.
It is a module convention. The module's own `task_spawn()` calls it after
constructing the object.

Work items are commonly triggered in three ways:

- `ScheduleNow()` enqueues `Run()` immediately.
- `ScheduleDelayed()` or `ScheduleOnInterval()` uses the high-resolution timer
  to enqueue a later run.
- uORB callback subscriptions enqueue the work item when a topic is published.

Examples:

- `src/examples/work_item/WorkItemExample.cpp`
- `src/modules/mc_rate_control/MulticopterRateControl.cpp`
- `src/modules/control_allocator/ControlAllocator.cpp`
- `src/modules/manual_control/ManualControl.cpp`

## Run-to-Completion Semantics

`WorkItem::Run()` is run-to-completion with respect to its work queue:

```text
WorkItem A::Run() starts
  ...
WorkItem A::Run() returns
then WorkItem B::Run() can run on the same queue
```

PX4 will not run another item on the same work queue until the current `Run()`
returns. The OS can still preempt the work queue thread with interrupts or
higher-priority threads, and work items on other queues can run concurrently.

`Run()` does not have a private stack. It runs on the shared work queue thread
stack. Local variables are gone when `Run()` returns; persistent state must live
in member variables owned by the module object.

```cpp
void MyController::Run()
{
    float error = compute_error();      // temporary
    _integrator += error * _dt;         // persistent member state
    publish_output(_integrator);
}
```

Avoid static local state unless it is intentionally shared across all instances.
Member variables are usually the correct place for filters, integrators, last
timestamps, uORB subscriptions, publications, and parameter state.

## Blocking Rules

A work item can technically block, because it is ordinary C++ running in an OS
thread. It should not block in normal flight-control code.

If a work item blocks, every other item sharing that queue is delayed:

```text
wq:rate_ctrl
  mc_rate_control::Run() blocks
  control_allocator::Run() waits behind it
```

Work item `Run()` methods should be:

- short
- non-blocking
- bounded in execution time
- careful with locks
- careful with I/O
- structured to do one step, publish results, and return

Use a dedicated thread if the design needs blocking waits, slow I/O, or a
long-running loop.

## Choosing a Model

Use a work queue when:

- the module reacts to uORB updates or periodic timers
- the runtime is short and predictable
- blocking is not needed
- sharing a queue is acceptable
- low thread count and lower memory use matter

Use a dedicated thread when:

- the module blocks in `px4_poll()`, serial reads, file I/O, or sleeps
- the module has long or unpredictable work
- delaying other modules on a shared queue would be unsafe
- the module needs its own stack or independent scheduling behavior

## Common Queues

The queue names and priorities are configured through `wq_config_t`:

```cpp
struct wq_config_t {
    const char *name;
    uint16_t stacksize;
    int8_t relative_priority;
};
```

Common queues include:

- `wq:rate_ctrl` for high-rate control work.
- `wq:nav_and_controllers` for navigation and controller work below rate-control
  priority.
- `wq:hp_default` for general high-priority work.
- `wq:lp_default` for lower-priority background work.
- `wq:INS0` through `wq:INS3` for estimator and IMU-instance work.
- bus-specific queues such as `wq:SPI*`, `wq:I2C*`, and `wq:tty*`.

Items on the same queue execute serially. Items on different queues may execute
concurrently, subject to OS priorities.

## Runtime Inspection

On a running PX4 target:

```sh
top
```

shows OS tasks and threads, including dedicated module tasks and active work
queue threads.

```sh
work_queue status
```

prints the active PX4 work queues and the work items attached to each queue,
including approximate run rates and intervals.

Module-specific status is available through:

```sh
<module> status
```

The total number of tasks and threads is target- and runtime-dependent. Startup
parameters, enabled drivers, active sensors, MAVLink links, and simulation mode
can all change which dedicated tasks and work queue threads exist.
