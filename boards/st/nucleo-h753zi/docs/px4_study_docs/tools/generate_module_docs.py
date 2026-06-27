#!/usr/bin/env python3
"""Generate architecture study docs for PX4 modules.

The generator is intentionally source-inventory based. It does not try to
reverse-engineer every branch in each module. Instead it extracts the stable
architecture signals that are useful for module study: build metadata, entry
points, classes, uORB topics, parameters, state-like enums, and source layout.
"""

from __future__ import annotations

import html
import re
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


SCRIPT_DIR = Path(__file__).resolve().parent


def find_repo_root(start: Path) -> Path:
    for parent in (start, *start.parents):
        if (parent / ".git").exists() and (parent / "src" / "modules").is_dir():
            return parent
    raise RuntimeError("could not locate PX4 repository root")


ROOT = find_repo_root(SCRIPT_DIR)
SRC_ROOT = ROOT / "src" / "modules"
OUT_ROOT = SCRIPT_DIR.parent
MODULE_OUT = OUT_ROOT / "modules"

EXCLUDED_PARTS = {
    ".git",
    "build",
    "test",
    "tests",
    "Micro-XRCE-DDS-Client",
    "Micro-XRCE-DDS-Client-v3",
    "zenoh-pico",
}

SOURCE_SUFFIXES = {".c", ".cc", ".cpp", ".h", ".hpp", ".hh", ".yaml", ".yml"}

CMAKE_KEYS = {
    "MODULE",
    "MAIN",
    "STACK_MAIN",
    "COMPILE_FLAGS",
    "SRCS",
    "MODULE_CONFIG",
    "DEPENDS",
    "INCLUDES",
    "EXTERNAL",
}

PALETTES = [
    {
        "name": "mist",
        "primary": "#f1f3f5",
        "secondary": "#e9ecef",
        "tertiary": "#f8f9fa",
        "accent": "#dee2e6",
        "line": "#6c757d",
        "dark": "#343a40",
        "text": "#212529",
    },
    {
        "name": "graphite",
        "primary": "#edf2f4",
        "secondary": "#d9dee2",
        "tertiary": "#f7f9fa",
        "accent": "#cfd4d8",
        "line": "#5c636a",
        "dark": "#2f3437",
        "text": "#1f2326",
    },
    {
        "name": "slate",
        "primary": "#eef0f2",
        "secondary": "#e1e5e8",
        "tertiary": "#fafafa",
        "accent": "#d5dade",
        "line": "#59636e",
        "dark": "#30363d",
        "text": "#202428",
    },
    {
        "name": "ash",
        "primary": "#f2f2f2",
        "secondary": "#e6e6e6",
        "tertiary": "#fbfbfb",
        "accent": "#d7d7d7",
        "line": "#707070",
        "dark": "#3d3d3d",
        "text": "#222222",
    },
]

ROLE_SUMMARIES = {
    "airship_att_control": "Controls airship attitude and converts attitude or rate demands into actuator-facing control outputs.",
    "airspeed_selector": "Selects, validates, and publishes the airspeed estimate that downstream fixed-wing control and navigation use.",
    "attitude_estimator_q": "Provides a lightweight quaternion attitude estimator using IMU and aiding data.",
    "battery_status": "Monitors battery measurements, estimates battery health and remaining energy, and publishes battery status.",
    "camera_feedback": "Processes camera trigger or capture feedback and reports camera capture timing to the rest of PX4.",
    "commander": "Owns the high-level vehicle state machine: arming, mode transitions, safety checks, failsafe coordination, and operator commands.",
    "control_allocator": "Maps normalized torque and thrust requests into actuator motor and servo setpoints using the configured vehicle geometry.",
    "dataman": "Provides persistent storage services for mission, geofence, rally point, and other structured data records.",
    "ekf2": "Runs the EKF2 estimator stack for attitude, velocity, position, sensor bias, and estimator status outputs.",
    "esc_battery": "Uses ESC telemetry to derive battery-like power status when ESC data is the available energy source.",
    "events": "Collects and forwards PX4 event messages for logging, MAVLink, and ground-station visibility.",
    "flight_mode_manager": "Selects and runs multicopter flight-mode tasks that generate trajectory and control setpoints.",
    "fw_att_control": "Runs fixed-wing attitude control and produces fixed-wing torque or actuator control demands.",
    "fw_autotune_attitude_control": "Injects and evaluates fixed-wing attitude-control excitation to support automatic gain tuning.",
    "fw_lateral_longitudinal_control": "Runs fixed-wing lateral and longitudinal control from navigation setpoints to attitude and thrust requests.",
    "fw_mode_manager": "Selects fixed-wing mode behavior and generates fixed-wing trajectory or attitude setpoints.",
    "fw_rate_control": "Runs fixed-wing angular-rate control and publishes actuator-facing torque/control outputs.",
    "gimbal": "Manages gimbal control commands, gimbal device status, and mount orientation setpoints.",
    "gyro_calibration": "Coordinates gyro calibration data collection and calibration result publication.",
    "gyro_fft": "Analyzes gyro vibration content using FFT processing and publishes diagnostic vibration information.",
    "hardfault_stream": "Streams hardfault information so crash data can be retrieved after a fault.",
    "internal_combustion_engine_control": "Controls internal-combustion-engine state and publishes engine status for vehicles that use an ICE.",
    "land_detector": "Determines whether the vehicle is landed, maybe landed, or airborne for failsafe and controller behavior.",
    "landing_target_estimator": "Estimates relative landing-target position from target observations and vehicle state.",
    "load_mon": "Reports CPU and system load so runtime health can be monitored.",
    "local_position_estimator": "Provides the legacy local-position estimator path using sensor and aiding inputs.",
    "logger": "Records selected uORB topics and system metadata into PX4 log files.",
    "mag_bias_estimator": "Estimates magnetometer bias and publishes bias corrections for estimator use.",
    "manual_control": "Selects valid manual input sources and publishes normalized manual stick and switch setpoints.",
    "mavlink": "Implements MAVLink telemetry, command, mission, parameter, and shell communication links.",
    "mc_att_control": "Runs multicopter attitude control and converts attitude setpoints into body-rate setpoints.",
    "mc_autotune_attitude_control": "Runs multicopter attitude-control excitation and analysis for automatic tuning.",
    "mc_hover_thrust_estimator": "Estimates the hover thrust needed by the multicopter position controller.",
    "mc_nn_control": "Runs an experimental neural-network multicopter control path.",
    "mc_pos_control": "Runs multicopter position and velocity control and publishes attitude/thrust setpoints.",
    "mc_raptor": "Runs an experimental multicopter Raptor control path for advanced setpoint generation.",
    "mc_rate_control": "Runs the high-rate multicopter body-rate controller and publishes torque and thrust setpoints.",
    "muorb": "Contains multi-uORB transport support code and nested module targets.",
    "muorb/apps": "Provides the application-side multi-uORB bridge target.",
    "muorb/slpi": "Provides the SLPI-side multi-uORB bridge target.",
    "navigator": "Owns mission, geofence, return, takeoff, landing, and other autonomous navigation behaviors.",
    "payload_deliverer": "Controls payload delivery or gripper-style release actions from vehicle commands.",
    "px4iofirmware": "Builds PX4IO firmware support code for the IO co-processor path.",
    "rc_update": "Converts raw RC input into calibrated manual-control input topics.",
    "replay": "Replays logged sensor and uORB data through PX4 modules for estimator and analysis workflows.",
    "rover_ackermann": "Controls Ackermann-steered rover motion from rover setpoints to actuator commands.",
    "rover_differential": "Controls differential-drive rover motion from rover setpoints to actuator commands.",
    "rover_mecanum": "Controls mecanum-drive rover motion from rover setpoints to wheel commands.",
    "sensors": "Aggregates, validates, prioritizes, and republishes raw sensor data into vehicle sensor topics.",
    "simulation": "Groups simulation-related module targets and shared simulation support.",
    "simulation/battery_simulator": "Simulates battery behavior for software-in-the-loop and hardware-in-the-loop runs.",
    "simulation/gz_bridge": "Bridges PX4 uORB data with Gazebo transport for simulation.",
    "simulation/pwm_out_sim": "Simulates PWM output behavior for HIL and simulator actuator paths.",
    "simulation/sensor_agp_sim": "Simulates airspeed or auxiliary pressure sensor data for simulation workflows.",
    "simulation/sensor_airspeed_sim": "Simulates airspeed sensor data for simulation workflows.",
    "simulation/sensor_baro_sim": "Simulates barometer data for simulation workflows.",
    "simulation/sensor_gps_sim": "Simulates GPS data for simulation workflows.",
    "simulation/sensor_mag_sim": "Simulates magnetometer data for simulation workflows.",
    "simulation/simulator_mavlink": "Connects PX4 to a MAVLink-based simulator backend.",
    "simulation/simulator_sih": "Runs the simple simulator-in-hardware vehicle dynamics model.",
    "simulation/system_power_simulator": "Simulates system power status for simulation workflows.",
    "spacecraft": "Runs spacecraft-specific attitude, rate, and actuator-control behavior.",
    "task_watchdog": "Watches registered tasks for missed heartbeats or runtime stalls.",
    "temperature_compensation": "Applies temperature compensation data to sensor correction paths.",
    "time_persistor": "Persists time information across boots when supported by the platform.",
    "uuv_att_control": "Runs underwater-vehicle attitude control.",
    "uuv_pos_control": "Runs underwater-vehicle position control.",
    "uxrce_dds_client": "Bridges PX4 uORB data to DDS through the Micro XRCE-DDS client.",
    "vision_target_estimator": "Estimates visual target state from perception observations and vehicle motion.",
    "vtol_att_control": "Coordinates VTOL attitude-control behavior and transitions between multicopter and fixed-wing control.",
    "zenoh": "Bridges PX4 data through Zenoh transport.",
}


@dataclass
class CMakeInfo:
    build_kind: str
    target: str
    main: str
    stack_main: str
    sources: list[str]
    module_config: str
    depends: list[str]


@dataclass
class ClassInfo:
    name: str
    base: str
    file: str


@dataclass
class ModuleInfo:
    path: Path
    rel: str
    slug: str
    title: str
    palette: dict[str, str]
    cmake: CMakeInfo
    description: str
    files: list[Path]
    source_files: list[Path]
    headers: list[Path]
    configs: list[Path]
    subscriptions: list[str]
    publications: list[str]
    topics: list[str]
    parameters: list[str]
    classes: list[ClassInfo]
    structs: list[ClassInfo]
    enums: list[str]
    states: list[str]
    child_modules: list[str]


def should_skip(path: Path) -> bool:
    return any(part in EXCLUDED_PARTS for part in path.parts)


def rel(path: Path) -> str:
    return path.relative_to(ROOT).as_posix()


def rel_to_module(module_path: Path, path: Path) -> str:
    return path.relative_to(module_path).as_posix()


def sanitize_id(value: str) -> str:
    safe = re.sub(r"[^A-Za-z0-9_]", "_", value)
    if not safe or safe[0].isdigit():
        safe = f"n_{safe}"
    return safe


def md_escape(value: str) -> str:
    return value.replace("|", "\\|").replace("\n", " ")


def html_escape(value: str) -> str:
    return html.escape(value, quote=True)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return ""


def strip_cmake_comments(text: str) -> str:
    out: list[str] = []
    for line in text.splitlines():
        out.append(line.split("#", 1)[0])
    return "\n".join(out)


def first_call_block(text: str, call_name: str) -> str:
    idx = text.find(call_name)
    if idx < 0:
        return ""
    open_idx = text.find("(", idx)
    if open_idx < 0:
        return ""
    depth = 0
    for pos in range(open_idx, len(text)):
        char = text[pos]
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth == 0:
                return text[open_idx + 1 : pos]
    return ""


def parse_cmake(module_path: Path) -> CMakeInfo:
    cmake_path = module_path / "CMakeLists.txt"
    text = strip_cmake_comments(read_text(cmake_path))
    build_kind = "directory"
    block = ""

    for call, kind in (
        ("px4_add_module", "px4 module"),
        ("add_library", "library"),
        ("px4_add_library", "library"),
        ("add_executable", "executable"),
    ):
        block = first_call_block(text, call)
        if block:
            build_kind = kind
            break

    tokens = re.findall(r'"[^"]+"|\$\{[^}]+\}|[^\s()]+', block)
    tokens = [token.strip('"') for token in tokens]
    sections: dict[str, list[str]] = {key: [] for key in CMAKE_KEYS}
    positional: list[str] = []
    key = ""

    for token in tokens:
        if token in CMAKE_KEYS:
            key = token
            continue
        if key:
            sections[key].append(token)
        else:
            positional.append(token)

    target = first_value(sections["MODULE"], positional[0] if positional else module_path.name)
    main = first_value(sections["MAIN"], target)
    stack_main = first_value(sections["STACK_MAIN"], "")
    sources = [value for value in sections["SRCS"] if not value.startswith("${")]
    module_config = first_value([value for value in sections["MODULE_CONFIG"] if not value.startswith("${")], "")
    depends = [value for value in sections["DEPENDS"] if value not in {"PRIVATE", "PUBLIC", "INTERFACE"}]

    return CMakeInfo(
        build_kind=build_kind,
        target=target,
        main=main,
        stack_main=stack_main,
        sources=sources,
        module_config=module_config,
        depends=depends,
    )


def first_value(values: list[str], default: str) -> str:
    for value in values:
        if value:
            return value
    return default


def find_module_paths() -> list[Path]:
    targets: set[Path] = {path for path in SRC_ROOT.iterdir() if path.is_dir() and not should_skip(path)}

    for cmake_path in SRC_ROOT.rglob("CMakeLists.txt"):
        if should_skip(cmake_path):
            continue
        text = read_text(cmake_path)
        if "px4_add_module" in text:
            targets.add(cmake_path.parent)

    return sorted(targets, key=lambda item: item.relative_to(SRC_ROOT).as_posix())


def collect_files(module_path: Path) -> list[Path]:
    files: list[Path] = []
    for path in module_path.rglob("*"):
        if should_skip(path):
            continue
        if path.is_file() and (path.suffix in SOURCE_SUFFIXES or path.name in {"CMakeLists.txt", "README.md"}):
            files.append(path)
    return sorted(files, key=lambda item: item.relative_to(module_path).as_posix())


def child_modules(module_path: Path, all_modules: Iterable[Path]) -> list[str]:
    children = []
    for candidate in all_modules:
        if candidate == module_path:
            continue
        try:
            child_rel = candidate.relative_to(module_path)
        except ValueError:
            continue
        if child_rel.parts:
            children.append(child_rel.as_posix())
    return sorted(children)


def clean_description_text(value: str, limit: int = 520) -> str:
    text = value.replace("\r", "\n")
    text = re.sub(r"^\s*#+\s*Description\s*$", "", text, flags=re.MULTILINE | re.IGNORECASE)
    text = re.sub(r"^\s*#+\s*[A-Za-z0-9 _/-]+\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\s+", " ", text).strip()
    return text[:limit].strip()


def description_from_print_macros(module_path: Path) -> str:
    raw_re = re.compile(r'PRINT_MODULE_DESCRIPTION\s*\(\s*R"([A-Za-z0-9_]*)\((.*?)\)\1"', re.DOTALL)

    for path in sorted(module_path.iterdir()):
        if not path.is_file() or should_skip(path) or path.suffix not in {".c", ".cc", ".cpp", ".h", ".hpp", ".hh"}:
            continue

        text = read_text(path)
        for match in raw_re.finditer(text):
            description = clean_description_text(match.group(2))
            if description:
                return description

    return ""


def description_from_files(module_path: Path) -> str:
    module_yaml = module_path / "module.yaml"
    if module_yaml.exists():
        text = read_text(module_yaml)
        for key in ("description", "short_desc", "module_description"):
            match = re.search(rf"^{key}\s*:\s*(.+)$", text, re.MULTILINE)
            if match:
                return match.group(1).strip().strip('"')
        match = re.search(r"^module_name\s*:\s*(.+)$", text, re.MULTILINE)
        if match:
            name = match.group(1).strip().strip('"')
            return f"Architecture notes for the {name} module."

    print_description = description_from_print_macros(module_path)
    if print_description:
        return print_description

    readme = module_path / "README.md"
    if readme.exists():
        lines = [
            line.strip()
            for line in read_text(readme).splitlines()
            if line.strip() and not line.lstrip().startswith("#")
        ]
        if lines:
            return lines[0][:240]

    return "Source-derived architecture notes for this PX4 module directory."


def topic_context(line: str) -> tuple[set[str], set[str], set[str]]:
    all_topics = set(re.findall(r"ORB_ID\(([^)]+)\)", line))
    all_topics.update(re.findall(r"uORB/topics/([A-Za-z0-9_]+)\.h", line))
    cleaned = {topic.strip() for topic in all_topics if re.match(r"^[A-Za-z0-9_]+$", topic.strip())}

    lower = line.lower()
    pubs: set[str] = set()
    subs: set[str] = set()
    if cleaned:
        if "publication" in lower or "publish" in lower or "orb_advert" in lower or "_pub" in lower:
            pubs.update(cleaned)
        if "subscription" in lower or "subscribe" in lower or "orb_subscribe" in lower or "_sub" in lower:
            subs.update(cleaned)
    return cleaned, pubs, subs


def extract_topics(files: list[Path]) -> tuple[list[str], list[str], list[str]]:
    topics: set[str] = set()
    pubs: set[str] = set()
    subs: set[str] = set()

    for path in files:
        if path.suffix not in {".c", ".cc", ".cpp", ".h", ".hpp", ".hh"}:
            continue
        for line in read_text(path).splitlines():
            line_topics, line_pubs, line_subs = topic_context(line)
            topics.update(line_topics)
            pubs.update(line_pubs)
            subs.update(line_subs)

    return sorted(subs), sorted(pubs), sorted(topics)


def extract_parameters(files: list[Path]) -> list[str]:
    params: set[str] = set()
    for path in files:
        text = read_text(path)
        params.update(re.findall(r"PARAM_DEFINE_[A-Z0-9_]+\(\s*([A-Z0-9_]+)", text))
        params.update(re.findall(r"\bPARAM_DEFINE_STRUCT\(\s*([A-Z0-9_]+)", text))
        if path.name == "module.yaml":
            params.update(re.findall(r"^\s*[-]?\s*name\s*:\s*([A-Z][A-Z0-9_]+)\s*$", text, re.MULTILINE))
            params.update(
                name.replace("${i}", "_i")
                for name in re.findall(r"^\s{8,}([A-Z][A-Z0-9_${}]+)\s*:", text, re.MULTILINE)
            )
    return sorted(params)


def extract_classes(files: list[Path], module_path: Path) -> tuple[list[ClassInfo], list[ClassInfo], list[str], list[str]]:
    classes: list[ClassInfo] = []
    structs: list[ClassInfo] = []
    enums: set[str] = set()
    states: set[str] = set()

    class_re = re.compile(r"\bclass\s+([A-Za-z_][A-Za-z0-9_]*)(?:\s*:\s*public\s+([A-Za-z_][A-Za-z0-9_:<>]*))?")
    struct_re = re.compile(r"\bstruct\s+([A-Za-z_][A-Za-z0-9_]*)")
    enum_re = re.compile(r"\benum(?:\s+class)?\s+([A-Za-z_][A-Za-z0-9_]*)")
    state_value_re = re.compile(r"\b([A-Z][A-Z0-9_]*(?:STATE|MODE|FAILSAFE|ARM|DISARM)[A-Z0-9_]*)\b")

    for path in files:
        if path.suffix not in {".c", ".cc", ".cpp", ".h", ".hpp", ".hh"}:
            continue
        text = read_text(path)
        path_rel = rel_to_module(module_path, path)

        for match in class_re.finditer(text):
            name = match.group(1)
            if name in {"if", "for", "while", "switch"}:
                continue
            base = (match.group(2) or "").split("<", 1)[0].split("::")[-1]
            classes.append(ClassInfo(name=name, base=base, file=path_rel))

        for match in struct_re.finditer(text):
            name = match.group(1)
            if name in {"if", "for", "while", "switch"}:
                continue
            structs.append(ClassInfo(name=name, base="", file=path_rel))

        for match in enum_re.finditer(text):
            enums.add(match.group(1))

        for match in state_value_re.finditer(text):
            states.add(match.group(1))

    return unique_classes(classes), unique_classes(structs), sorted(enums), sorted(states)


def unique_classes(items: list[ClassInfo]) -> list[ClassInfo]:
    seen: set[tuple[str, str]] = set()
    out: list[ClassInfo] = []
    for item in items:
        key = (item.name, item.file)
        if key in seen:
            continue
        seen.add(key)
        out.append(item)
    return out


def module_info(module_path: Path, index: int, all_modules: list[Path]) -> ModuleInfo:
    rel_path = module_path.relative_to(SRC_ROOT).as_posix()
    slug = rel_path.replace("/", "__")
    files = collect_files(module_path)
    sources = [path for path in files if path.suffix in {".c", ".cc", ".cpp"}]
    headers = [path for path in files if path.suffix in {".h", ".hpp", ".hh"}]
    configs = [path for path in files if path.suffix in {".yaml", ".yml"} or path.name == "CMakeLists.txt"]
    subscriptions, publications, topics = extract_topics(files)
    classes, structs, enums, states = extract_classes(files, module_path)

    return ModuleInfo(
        path=module_path,
        rel=rel(module_path),
        slug=slug,
        title=rel_path,
        palette=PALETTES[index % len(PALETTES)],
        cmake=parse_cmake(module_path),
        description=description_from_files(module_path),
        files=files,
        source_files=sources,
        headers=headers,
        configs=configs,
        subscriptions=subscriptions,
        publications=publications,
        topics=topics,
        parameters=extract_parameters(files),
        classes=classes,
        structs=structs,
        enums=enums,
        states=states,
        child_modules=child_modules(module_path, all_modules),
    )


def mermaid_init(info: ModuleInfo) -> str:
    p = info.palette
    return (
        '%%{init: {"theme":"base","themeVariables":{'
        f'"primaryColor":"{p["primary"]}",'
        f'"secondaryColor":"{p["secondary"]}",'
        f'"tertiaryColor":"{p["tertiary"]}",'
        f'"primaryBorderColor":"{p["line"]}",'
        f'"primaryTextColor":"{p["text"]}",'
        f'"lineColor":"{p["line"]}",'
        f'"fontFamily":"Inter, Arial, sans-serif"'
        "}}}%%"
    )


def class_defs(info: ModuleInfo) -> str:
    p = info.palette
    return "\n".join(
        [
            f"classDef module fill:{p['primary']},stroke:{p['dark']},color:{p['text']};",
            f"classDef io fill:{p['secondary']},stroke:{p['line']},color:{p['text']};",
            f"classDef data fill:{p['tertiary']},stroke:{p['line']},color:{p['text']};",
            f"classDef exec fill:{p['accent']},stroke:{p['dark']},color:{p['text']};",
        ]
    )


def node_label(value: str, max_len: int = 42) -> str:
    cleaned = value.replace('"', "'")
    if len(cleaned) > max_len:
        return cleaned[: max_len - 3] + "..."
    return cleaned


def limited(values: list[str], limit: int) -> list[str]:
    return values[:limit]


def architecture_diagram(info: ModuleInfo) -> str:
    lines = [mermaid_init(info), "flowchart LR"]
    lines.append(f'  Module["{node_label(info.title)}"]:::module')
    lines.append(f'  Build["{node_label(info.cmake.build_kind + ": " + info.cmake.target)}"]:::data')
    lines.append('  Params["parameters / module.yaml"]:::data')
    lines.append('  Schedule["task, work queue, or callback"]:::exec')

    inputs = limited(info.subscriptions or info.topics, 6)
    outputs = limited(info.publications, 6)

    if inputs:
        lines.append("  subgraph Inputs")
        for idx, topic in enumerate(inputs):
            lines.append(f'    In{idx}["{node_label(topic)}"]:::io')
        lines.append("  end")
    else:
        lines.append('  In0["no input topics detected"]:::io')
        inputs = ["In0"]

    if outputs:
        lines.append("  subgraph Outputs")
        for idx, topic in enumerate(outputs):
            lines.append(f'    Out{idx}["{node_label(topic)}"]:::io')
        lines.append("  end")
    else:
        lines.append('  Out0["no output topics detected"]:::io')
        outputs = ["Out0"]

    if info.subscriptions or info.topics:
        for idx, _ in enumerate(limited(info.subscriptions or info.topics, 6)):
            lines.append(f"  In{idx} --> Module")
    else:
        lines.append("  In0 -.-> Module")

    lines.append("  Build --> Module")
    lines.append("  Params --> Module")
    lines.append("  Schedule --> Module")

    if info.publications:
        for idx, _ in enumerate(limited(info.publications, 6)):
            lines.append(f"  Module --> Out{idx}")
    else:
        lines.append("  Module -.-> Out0")

    lines.append(class_defs(info))
    return "\n".join(lines)


def data_flow_diagram(info: ModuleInfo) -> str:
    lines = [mermaid_init(info), "flowchart LR"]
    lines.extend(
        [
            '  UORBIn["uORB subscriptions"]:::io',
            '  Params["parameter cache"]:::data',
            '  Update["input update / polling"]:::exec',
            f'  Logic["{node_label(info.cmake.main or info.cmake.target)} logic"]:::module',
            '  UORBOut["uORB publications"]:::io',
            '  Status["status, events, perf counters"]:::data',
            "  UORBIn --> Update",
            "  Params --> Logic",
            "  Update --> Logic",
            "  Logic --> UORBOut",
            "  Logic --> Status",
        ]
    )

    for idx, topic in enumerate(limited(info.subscriptions, 5)):
        lines.append(f'  Sub{idx}["{node_label(topic)}"]:::io --> UORBIn')
    for idx, topic in enumerate(limited(info.publications, 5)):
        lines.append(f'  UORBOut --> Pub{idx}["{node_label(topic)}"]:::io')

    lines.append(class_defs(info))
    return "\n".join(lines)


def execution_flow_diagram(info: ModuleInfo) -> str:
    main = info.cmake.main or info.cmake.target
    lines = [mermaid_init(info), "flowchart TD"]
    lines.extend(
        [
            f'  Start["px4 {node_label(main)} start"]:::exec',
            '  Spawn["task_spawn / instantiate"]:::exec',
            '  Init["init subscriptions, publishers, parameters"]:::module',
            '  Schedule["schedule work item or enter task loop"]:::exec',
            '  Poll["poll, callback, or interval tick"]:::exec',
            '  Update["copy inputs and update parameters"]:::module',
            '  Compute["run control, estimation, bridge, or service logic"]:::module',
            '  Publish["publish outputs / events / status"]:::io',
            '  Stop{"stop requested?"}:::data',
            '  Exit["cleanup and exit"]:::exec',
            "  Start --> Spawn --> Init --> Schedule --> Poll --> Update --> Compute --> Publish --> Stop",
            "  Stop -- no --> Poll",
            "  Stop -- yes --> Exit",
        ]
    )
    lines.append(class_defs(info))
    return "\n".join(lines)


def state_machine_diagram(info: ModuleInfo) -> str:
    lines = [mermaid_init(info), "stateDiagram-v2"]
    detected = limited(info.states, 6)
    if detected:
        lines.append("  [*] --> Created")
        lines.append("  Created --> Initialized: start")
        previous = "Initialized"
        for idx, state in enumerate(detected):
            state_id = f"S{idx}"
            lines.append(f'  {state_id}: {node_label(state, 28)}')
            lines.append(f"  {previous} --> {state_id}: detected state path")
            previous = state_id
        lines.append(f"  {previous} --> Running: normal execution")
        lines.append("  Running --> Stopped: stop")
        lines.append("  Stopped --> [*]")
    else:
        lines.extend(
            [
                "  [*] --> Created",
                "  Created --> Initialized: start",
                "  Initialized --> Running: init complete",
                "  Running --> Updating: new data or timer",
                "  Updating --> Publishing: output ready",
                "  Publishing --> Running: wait next cycle",
                "  Running --> Error: health or IO failure",
                "  Error --> Running: recovered",
                "  Running --> Stopped: stop",
                "  Stopped --> [*]",
            ]
        )
    return "\n".join(lines)


def sequence_diagram(info: ModuleInfo) -> str:
    main = info.cmake.main or info.cmake.target
    lines = [mermaid_init(info), "sequenceDiagram"]
    lines.extend(
        [
            "  participant CLI as px4 shell",
            f"  participant M as {node_label(main, 30)}",
            "  participant P as Parameters",
            "  participant U as uORB",
            "  participant W as Scheduler",
            f"  CLI->>M: start {node_label(main, 28)}",
            "  M->>P: load cached parameter values",
            "  M->>U: advertise and subscribe topics",
            "  M->>W: schedule task or work item",
            "  loop execution cycle",
            "    W-->>M: timer, callback, or poll wakeup",
            "    U-->>M: input topic samples",
            "    M->>P: consume parameter updates",
            "    M->>M: validate, compute, and update state",
            "    M-->>U: publish outputs and status",
            "  end",
            "  CLI->>M: status / stop",
        ]
    )
    return "\n".join(lines)


def class_diagram(info: ModuleInfo) -> str:
    lines = [mermaid_init(info), "classDiagram"]
    items = limited(info.classes, 16)
    if not items:
        class_name = sanitize_id(info.cmake.target or info.slug)
        lines.append(f"  class {class_name}")
        lines.append(f"  {class_name} : {info.cmake.build_kind}")
        lines.append(f"  {class_name} : classes not detected")
        return "\n".join(lines)

    used: set[str] = set()
    for item in items:
        class_name = sanitize_id(item.name)
        if class_name in used:
            class_name = sanitize_id(f"{item.name}_{len(used)}")
        used.add(class_name)
        lines.append(f"  class {class_name}")
        lines.append(f"  {class_name} : {node_label(item.file, 54)}")
        if item.base:
            base = sanitize_id(item.base)
            lines.append(f"  class {base}")
            lines.append(f"  {base} <|-- {class_name}")
    return "\n".join(lines)


def list_text(values: list[str], empty: str = "None detected.", limit: int = 24) -> str:
    if not values:
        return f"- {empty}"
    out = [f"- `{value}`" for value in values[:limit]]
    if len(values) > limit:
        out.append(f"- ... {len(values) - limit} more")
    return "\n".join(out)


def md_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        rows = [["None detected." for _ in headers]]
    out = ["| " + " | ".join(headers) + " |"]
    out.append("| " + " | ".join("---" for _ in headers) + " |")
    for row in rows:
        padded = row + [""] * (len(headers) - len(row))
        out.append("| " + " | ".join(md_escape(value) for value in padded[: len(headers)]) + " |")
    return "\n".join(out)


def html_table(headers: list[str], rows: list[list[str]]) -> str:
    if not rows:
        rows = [["None detected." for _ in headers]]
    head = "".join(f"<th>{html_escape(header)}</th>" for header in headers)
    body_rows = []
    for row in rows:
        padded = row + [""] * (len(headers) - len(row))
        cells = "".join(f"<td>{html_escape(value)}</td>" for value in padded[: len(headers)])
        body_rows.append(f"<tr>{cells}</tr>")
    return f"<table><thead><tr>{head}</tr></thead><tbody>{''.join(body_rows)}</tbody></table>"


def source_rows(info: ModuleInfo, limit: int = 40) -> list[list[str]]:
    rows: list[list[str]] = []
    for path in info.files[:limit]:
        kind = "source"
        if path.suffix in {".h", ".hpp", ".hh"}:
            kind = "header"
        elif path.suffix in {".yaml", ".yml"}:
            kind = "config"
        elif path.name == "CMakeLists.txt":
            kind = "build"
        elif path.name == "README.md":
            kind = "readme"
        rows.append([rel_to_module(info.path, path), kind])
    if len(info.files) > limit:
        rows.append([f"... {len(info.files) - limit} more files", "omitted"])
    return rows


def build_rows(info: ModuleInfo) -> list[list[str]]:
    return [
        ["Module path", info.rel],
        ["Build kind", info.cmake.build_kind],
        ["Build target", info.cmake.target],
        ["Runtime main", info.cmake.main],
        ["Stack main", info.cmake.stack_main or "Not specified"],
        ["Module config", info.cmake.module_config or "Not specified"],
        ["Detected sources", str(len(info.source_files))],
        ["Detected headers", str(len(info.headers))],
        ["Detected configs", str(len(info.configs))],
    ]


def class_rows(info: ModuleInfo) -> list[list[str]]:
    rows = [[item.name, item.base or "", item.file] for item in info.classes[:24]]
    if len(info.classes) > 24:
        rows.append([f"... {len(info.classes) - 24} more", "", ""])
    return rows


def topic_rows(info: ModuleInfo) -> list[list[str]]:
    rows: list[list[str]] = []
    all_names = sorted(set(info.topics) | set(info.subscriptions) | set(info.publications))
    for topic in all_names[:48]:
        direction = []
        if topic in info.subscriptions:
            direction.append("subscribed")
        if topic in info.publications:
            direction.append("published")
        if not direction:
            direction.append("referenced")
        rows.append([topic, ", ".join(direction)])
    if len(all_names) > 48:
        rows.append([f"... {len(all_names) - 48} more topics", "omitted"])
    return rows


def human_list(values: list[str], limit: int = 8) -> str:
    if not values:
        return "none detected"
    shown = [f"`{value}`" for value in values[:limit]]
    if len(values) > limit:
        shown.append(f"... {len(values) - limit} more")
    return ", ".join(shown)


def source_text(info: ModuleInfo) -> str:
    chunks: list[str] = []
    for path in info.source_files + info.headers:
        chunks.append(read_text(path))
    return "\n".join(chunks)


def role_summary(info: ModuleInfo) -> str:
    if info.title in ROLE_SUMMARIES:
        return ROLE_SUMMARIES[info.title]

    if info.child_modules:
        return f"Groups nested PX4 module targets under `{info.title}` and provides shared source or configuration context for those children."

    useful_description = info.description
    if useful_description and "Source-derived architecture notes" not in useful_description:
        return useful_description

    if "control" in info.title:
        return f"Runs control logic for the `{info.title}` vehicle or subsystem path."
    if "estimator" in info.title:
        return f"Estimates state for the `{info.title}` subsystem from uORB inputs and configuration parameters."
    if "sim" in info.title or "simulation" in info.title:
        return f"Provides simulation support for the `{info.title}` path."

    return f"Implements the PX4 `{info.title}` module and its runtime data-flow responsibilities."


def inferred_domain_responsibilities(info: ModuleInfo) -> list[str]:
    title = info.title.lower()
    responsibilities: list[str] = []

    if "control" in title or "_ctl" in title:
        responsibilities.append("Convert selected state estimates and setpoints into downstream control or actuator-facing setpoints.")
    if "estimator" in title or "ekf" in title:
        responsibilities.append("Fuse, filter, or validate measurements into estimated state outputs for other modules.")
    if "sim" in title or "simulation" in title:
        responsibilities.append("Generate simulator-facing or simulated sensor/actuator data for non-flight-hardware runs.")
    if any(token in title for token in ("mavlink", "uxrce", "zenoh", "muorb", "bridge")):
        responsibilities.append("Translate between PX4 uORB data and an external transport or companion-computer interface.")
    if "logger" in title or "replay" in title or "dataman" in title:
        responsibilities.append("Provide persistence, replay, or data-recording services used by other PX4 modules.")
    if "commander" in title or "navigator" in title or "mode_manager" in title:
        responsibilities.append("Coordinate higher-level vehicle behavior rather than directly driving actuators.")
    if "sensor" in title or title == "sensors":
        responsibilities.append("Publish or condition sensor topics consumed by estimators and controllers.")

    return responsibilities


def responsibility_bullets(info: ModuleInfo) -> list[str]:
    bullets = inferred_domain_responsibilities(info)

    if info.subscriptions:
        bullets.append(f"Consume runtime inputs from uORB topics such as {human_list(info.subscriptions)}.")
    elif info.topics:
        bullets.append(f"Reference uORB topics such as {human_list(info.topics)}.")
    else:
        bullets.append("Operate without directly detected uORB topic dependencies in this source inventory.")

    if info.publications:
        bullets.append(f"Publish outputs or status topics such as {human_list(info.publications)}.")
    else:
        bullets.append("Do not publish directly detected uORB outputs from this module directory.")

    if info.parameters:
        bullets.append(f"Use parameters or module configuration entries such as {human_list(info.parameters, limit=6)}.")
    elif info.cmake.module_config:
        bullets.append(f"Use module configuration from `{info.cmake.module_config}`.")
    else:
        config_files = [rel_to_module(info.path, path) for path in info.configs if path.suffix in {".yaml", ".yml"}]
        if config_files:
            bullets.append(f"Use module configuration files such as {human_list(config_files, limit=6)}.")

    if info.classes:
        bullets.append(f"Implement the main behavior in classes such as {human_list([item.name for item in info.classes], limit=6)}.")
    elif info.source_files:
        bullets.append("Implement behavior mostly in C/C++ source functions rather than detected C++ classes.")

    if info.child_modules:
        bullets.append(f"Organize nested module targets: {human_list(info.child_modules, limit=6)}.")

    deduped: list[str] = []
    for bullet in bullets:
        if bullet not in deduped:
            deduped.append(bullet)
    return deduped[:8]


def scheduling_bullets(info: ModuleInfo) -> list[str]:
    text = source_text(info)
    bullets: list[str] = []
    wq_names = sorted(set(re.findall(r"wq_configurations::([A-Za-z0-9_]+)", text)))
    uses_work_queue = any(token in text for token in ("ScheduledWorkItem", "WorkItem(", "OutputModuleInterface", "task_id_is_work_queue"))
    uses_task = "px4_task_spawn_cmd" in text

    if uses_work_queue:
        if wq_names:
            bullets.append(f"Runs work-queue callbacks on queue configurations such as {human_list(wq_names, limit=6)}.")
        else:
            bullets.append("Runs as a PX4 work item or output module on a shared work queue thread.")

    if uses_task:
        if uses_work_queue:
            bullets.append("Also contains explicit task-spawn code or helper task creation in this module tree.")
        else:
            bullets.append("Creates a dedicated PX4 task/thread with `px4_task_spawn_cmd()`.")

    if "run_trampoline_impl" in text or re.search(r"\bvoid\s+[A-Za-z0-9_:]+::run\s*\(", text):
        bullets.append("Uses a `run()` loop style module body for repeated execution.")
    if "registerCallback" in text:
        bullets.append("Uses uORB callback registration so new topic data can schedule execution.")
    if "ScheduleOnInterval" in text or "ScheduleDelayed" in text or "ScheduleNow" in text:
        bullets.append("Uses explicit work-item scheduling through immediate, delayed, or interval scheduling calls.")
    if "px4_poll" in text:
        bullets.append("Waits on file descriptors or uORB subscriptions with `px4_poll()`.")
    if "pthread_create" in text:
        bullets.append("Creates an additional pthread helper context.")

    if not bullets:
        bullets.append("Scheduling style was not explicit in the detected source inventory; inspect the entry source for runtime details.")

    return bullets


def interface_rows(info: ModuleInfo) -> list[list[str]]:
    config_details = human_list(info.parameters, limit=10)
    if not info.parameters:
        config_files = [rel_to_module(info.path, path) for path in info.configs if path.suffix in {".yaml", ".yml"}]
        config_details = info.cmake.module_config or human_list(config_files, limit=10)

    rows = [
        ["Primary inputs", human_list(info.subscriptions, limit=10)],
        ["Primary outputs", human_list(info.publications, limit=10)],
        ["Referenced topics", human_list(info.topics, limit=10)],
        ["Parameters/config", config_details],
        ["Key classes", human_list([item.name for item in info.classes], limit=10)],
    ]
    return rows


def source_landmark_rows(info: ModuleInfo) -> list[list[str]]:
    rows: list[list[str]] = []
    seen: set[str] = set()
    main = info.cmake.main

    for path in info.source_files:
        text = read_text(path)
        reason = ""
        if "ModuleBase::Descriptor" in text or "task_spawn" in text or f"{main}_main" in text:
            reason = "Entry point, start command, or module lifecycle code"
        elif "Run()" in text or "::Run(" in text:
            reason = "Work-item callback or main runtime update path"
        elif "run()" in text or "::run(" in text:
            reason = "Dedicated task loop or repeated runtime path"

        if reason:
            path_rel = rel_to_module(info.path, path)
            rows.append([path_rel, reason])
            seen.add(path_rel)
        if len(rows) >= 5:
            break

    for path in info.configs:
        path_rel = rel_to_module(info.path, path)
        if path_rel not in seen:
            rows.append([path_rel, "Build, parameter, or module configuration"])
            seen.add(path_rel)
        if len(rows) >= 7:
            break

    for item in info.classes[:4]:
        if item.file not in seen:
            rows.append([item.file, f"Defines `{item.name}` class"])
            seen.add(item.file)
        if len(rows) >= 8:
            break

    return rows


def markdown_bullets(values: list[str]) -> str:
    return "\n".join(f"- {value}" for value in values) if values else "- None detected."


def html_bullets(values: list[str]) -> str:
    if not values:
        return "<ul><li>None detected.</li></ul>"
    return "<ul>" + "".join(f"<li>{html_escape(value)}</li>" for value in values) + "</ul>"


def write_markdown(info: ModuleInfo) -> None:
    diagrams = {
        "Architecture": architecture_diagram(info),
        "Data Flow": data_flow_diagram(info),
        "Execution Flow": execution_flow_diagram(info),
        "State Machine": state_machine_diagram(info),
        "Sequence": sequence_diagram(info),
        "Class Diagram": class_diagram(info),
    }

    child_text = list_text(info.child_modules, "No nested module targets detected.")
    depends_text = list_text(info.cmake.depends, "No explicit CMake dependencies detected.")
    params_text = list_text(info.parameters, "No parameters detected.", limit=40)
    enum_text = list_text(info.enums, "No enums detected.", limit=32)
    state_text = list_text(info.states, "No state-like symbols detected.", limit=40)

    parts = [
        f"# PX4 Module Architecture: `{info.title}`",
        "",
        f"- Source: `{info.rel}`",
        f"- Build target: `{info.cmake.target}`",
        f"- Runtime main: `{info.cmake.main}`",
        f"- Build kind: `{info.cmake.build_kind}`",
        f"- Mermaid palette: `{info.palette['name']}` grey tone",
        "",
        info.description,
        "",
        "## Architecture Overview",
        "",
        "This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.",
        "",
        "```mermaid",
        diagrams["Architecture"],
        "```",
        "",
        "## Role, Functions, and Responsibilities",
        "",
        role_summary(info),
        "",
        "### Primary Responsibilities",
        "",
        markdown_bullets(responsibility_bullets(info)),
        "",
        "### Runtime Behavior",
        "",
        markdown_bullets(scheduling_bullets(info)),
        "",
        "### Main Interfaces",
        "",
        md_table(["Area", "Details"], interface_rows(info)),
        "",
        "### Source Landmarks",
        "",
        md_table(["File", "Why it matters"], source_landmark_rows(info)),
        "",
        "## Build and Entry Points",
        "",
        md_table(["Field", "Value"], build_rows(info)),
        "",
        "### CMake Dependencies",
        "",
        depends_text,
        "",
        "### Nested Module Targets",
        "",
        child_text,
        "",
        "## Data Flow",
        "",
        "```mermaid",
        diagrams["Data Flow"],
        "```",
        "",
        "### uORB Topics",
        "",
        md_table(["Topic", "Detected direction"], topic_rows(info)),
        "",
        "## Execution Flow",
        "",
        "```mermaid",
        diagrams["Execution Flow"],
        "```",
        "",
        "The common PX4 module lifecycle is command entry, object construction or task spawn, parameter loading, topic setup, scheduled execution, publication, status reporting, and stop/cleanup. Modules that use `ModuleBase`, `ScheduledWorkItem`, polling loops, or bridge callbacks still fit this lifecycle with different scheduling triggers.",
        "",
        "## State Machine",
        "",
        "```mermaid",
        diagrams["State Machine"],
        "```",
        "",
        "### Detected State-Like Symbols",
        "",
        state_text,
        "",
        "## Sequence Diagram",
        "",
        "```mermaid",
        diagrams["Sequence"],
        "```",
        "",
        "## Class Diagram",
        "",
        "```mermaid",
        diagrams["Class Diagram"],
        "```",
        "",
        "### Detected Classes",
        "",
        md_table(["Class", "Base", "File"], class_rows(info)),
        "",
        "### Detected Enums",
        "",
        enum_text,
        "",
        "## Parameters and Configuration",
        "",
        params_text,
        "",
        "## Source Map",
        "",
        md_table(["File", "Kind"], source_rows(info)),
        "",
        "## Review Notes",
        "",
        "- The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.",
        "- Topic direction is inferred from nearby source context such as `Subscription`, `Publication`, `orb_subscribe`, and `publish` usage.",
        "- When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.",
        "",
    ]

    (MODULE_OUT / f"{info.slug}.md").write_text("\n".join(parts), encoding="utf-8")


def page_css(info: ModuleInfo) -> str:
    p = info.palette
    return f"""
    :root {{
      --bg: #ffffff;
      --panel: {p['tertiary']};
      --soft: {p['primary']};
      --soft-2: {p['secondary']};
      --line: {p['line']};
      --text: {p['text']};
      --muted: #5f666d;
      --accent: {p['accent']};
      --dark: {p['dark']};
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--text);
      font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
      line-height: 1.5;
    }}
    header {{
      border-bottom: 1px solid var(--line);
      background: var(--soft);
      padding: 28px min(6vw, 56px);
    }}
    main {{
      max-width: 1180px;
      margin: 0 auto;
      padding: 28px min(5vw, 44px) 64px;
    }}
    h1 {{ margin: 0 0 8px; font-size: 30px; letter-spacing: 0; }}
    h2 {{ margin-top: 36px; padding-bottom: 6px; border-bottom: 1px solid var(--line); }}
    h3 {{ margin-top: 24px; }}
    a {{ color: #2f4f6f; }}
    code {{
      background: var(--soft-2);
      border: 1px solid #cfd4d8;
      border-radius: 4px;
      padding: 1px 5px;
      font-size: 0.92em;
    }}
    .meta {{
      display: grid;
      grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
      gap: 8px;
      margin-top: 16px;
    }}
    .meta div {{
      background: rgba(255, 255, 255, 0.62);
      border: 1px solid #cfd4d8;
      border-radius: 6px;
      padding: 8px 10px;
      min-width: 0;
    }}
    .section-note {{
      color: var(--muted);
      max-width: 940px;
    }}
    table {{
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0 24px;
      table-layout: auto;
    }}
    th, td {{
      border: 1px solid #d6dadd;
      padding: 8px 10px;
      vertical-align: top;
      overflow-wrap: anywhere;
    }}
    th {{ background: var(--soft-2); text-align: left; }}
    tr:nth-child(even) td {{ background: #fafafa; }}
    ul {{ padding-left: 22px; }}
    .diagram {{
      border: 1px solid #d6dadd;
      background: #fff;
      border-radius: 6px;
      padding: 16px;
      margin: 14px 0 24px;
      overflow-x: auto;
    }}
    .mermaid {{ min-width: 320px; }}
    .topnav {{ margin-bottom: 12px; color: var(--muted); }}
    .topnav a {{ margin-right: 14px; }}
    """


def html_list(values: list[str], empty: str = "None detected.", limit: int = 24) -> str:
    if not values:
        return f"<ul><li>{html_escape(empty)}</li></ul>"
    items = [f"<li><code>{html_escape(value)}</code></li>" for value in values[:limit]]
    if len(values) > limit:
        items.append(f"<li>... {len(values) - limit} more</li>")
    return "<ul>" + "".join(items) + "</ul>"


def diagram_block(diagram: str) -> str:
    return f'<div class="diagram"><pre class="mermaid">{html_escape(diagram)}</pre></div>'


def write_html(info: ModuleInfo) -> None:
    diagrams = {
        "Architecture": architecture_diagram(info),
        "Data Flow": data_flow_diagram(info),
        "Execution Flow": execution_flow_diagram(info),
        "State Machine": state_machine_diagram(info),
        "Sequence": sequence_diagram(info),
        "Class Diagram": class_diagram(info),
    }

    html_doc = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PX4 Module Architecture: {html_escape(info.title)}</title>
  <style>{page_css(info)}</style>
  <script type="module">
    import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
    mermaid.initialize({{ startOnLoad: true, securityLevel: 'loose' }});
  </script>
</head>
<body>
  <header>
    <div class="topnav"><a href="../index.html">Index</a><a href="{html_escape(info.slug)}.md">Markdown</a></div>
    <h1>PX4 Module Architecture: <code>{html_escape(info.title)}</code></h1>
    <p>{html_escape(info.description)}</p>
    <div class="meta">
      <div><strong>Source</strong><br><code>{html_escape(info.rel)}</code></div>
      <div><strong>Build target</strong><br><code>{html_escape(info.cmake.target)}</code></div>
      <div><strong>Runtime main</strong><br><code>{html_escape(info.cmake.main)}</code></div>
      <div><strong>Build kind</strong><br><code>{html_escape(info.cmake.build_kind)}</code></div>
      <div><strong>Mermaid palette</strong><br><code>{html_escape(info.palette['name'])}</code> grey tone</div>
    </div>
  </header>
  <main>
    <h2>Architecture Overview</h2>
    <p class="section-note">This page is generated from the module source tree and shows the stable architecture surfaces: build entry point, scheduling shape, uORB data interfaces, parameter/configuration surfaces, and C++ types found in the module.</p>
    {diagram_block(diagrams['Architecture'])}

    <h2>Role, Functions, and Responsibilities</h2>
    <p>{html_escape(role_summary(info))}</p>

    <h3>Primary Responsibilities</h3>
    {html_bullets(responsibility_bullets(info))}

    <h3>Runtime Behavior</h3>
    {html_bullets(scheduling_bullets(info))}

    <h3>Main Interfaces</h3>
    {html_table(['Area', 'Details'], interface_rows(info))}

    <h3>Source Landmarks</h3>
    {html_table(['File', 'Why it matters'], source_landmark_rows(info))}

    <h2>Build and Entry Points</h2>
    {html_table(['Field', 'Value'], build_rows(info))}

    <h3>CMake Dependencies</h3>
    {html_list(info.cmake.depends, 'No explicit CMake dependencies detected.')}

    <h3>Nested Module Targets</h3>
    {html_list(info.child_modules, 'No nested module targets detected.')}

    <h2>Data Flow</h2>
    {diagram_block(diagrams['Data Flow'])}
    <h3>uORB Topics</h3>
    {html_table(['Topic', 'Detected direction'], topic_rows(info))}

    <h2>Execution Flow</h2>
    {diagram_block(diagrams['Execution Flow'])}
    <p class="section-note">The common PX4 module lifecycle is command entry, object construction or task spawn, parameter loading, topic setup, scheduled execution, publication, status reporting, and stop/cleanup. Modules that use <code>ModuleBase</code>, <code>ScheduledWorkItem</code>, polling loops, or bridge callbacks still fit this lifecycle with different scheduling triggers.</p>

    <h2>State Machine</h2>
    {diagram_block(diagrams['State Machine'])}
    <h3>Detected State-Like Symbols</h3>
    {html_list(info.states, 'No state-like symbols detected.', limit=40)}

    <h2>Sequence Diagram</h2>
    {diagram_block(diagrams['Sequence'])}

    <h2>Class Diagram</h2>
    {diagram_block(diagrams['Class Diagram'])}
    <h3>Detected Classes</h3>
    {html_table(['Class', 'Base', 'File'], class_rows(info))}
    <h3>Detected Enums</h3>
    {html_list(info.enums, 'No enums detected.', limit=32)}

    <h2>Parameters and Configuration</h2>
    {html_list(info.parameters, 'No parameters detected.', limit=40)}

    <h2>Source Map</h2>
    {html_table(['File', 'Kind'], source_rows(info))}

    <h2>Review Notes</h2>
    <ul>
      <li>The diagrams are generated from static source inventory and should be used as a study map, not as a formal proof of every runtime branch.</li>
      <li>Topic direction is inferred from nearby source context such as <code>Subscription</code>, <code>Publication</code>, <code>orb_subscribe</code>, and <code>publish</code> usage.</li>
      <li>When a module has no explicit state enum, the state diagram shows the standard PX4 module lifecycle.</li>
    </ul>
  </main>
</body>
</html>
"""

    (MODULE_OUT / f"{info.slug}.html").write_text(html_doc, encoding="utf-8")


def write_index(infos: list[ModuleInfo]) -> None:
    md_rows = []
    for info in infos:
        md_rows.append(
            [
                f"[`{info.title}`](modules/{info.slug}.md)",
                f"[html](modules/{info.slug}.html)",
                info.cmake.build_kind,
                info.cmake.target,
                str(len(info.topics)),
                str(len(info.classes)),
            ]
        )

    index_md = "\n".join(
        [
            "# PX4 Study Docs",
            "",
            "Generated architecture study documents for `src/modules`.",
            "",
            f"- Module documentation targets: `{len(infos)}`",
            "- Scope: all immediate `src/modules/*` directories plus nested directories that declare `px4_add_module(...)`.",
            "- Outputs: one Markdown and one standalone HTML file per target.",
            "",
            md_table(["Module", "HTML", "Build kind", "Target", "Topics", "Classes"], md_rows),
            "",
        ]
    )
    (OUT_ROOT / "index.md").write_text(index_md, encoding="utf-8")

    rows = []
    for info in infos:
        rows.append(
            [
                f'<a href="modules/{html_escape(info.slug)}.html"><code>{html_escape(info.title)}</code></a>',
                info.cmake.build_kind,
                info.cmake.target,
                str(len(info.topics)),
                str(len(info.classes)),
            ]
        )

    html_rows = []
    for row in rows:
        html_rows.append("<tr>" + "".join(f"<td>{cell}</td>" for cell in row) + "</tr>")

    index_html = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>PX4 Study Docs</title>
  <style>
    body {{ margin: 0; font-family: Inter, ui-sans-serif, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; color: #212529; }}
    header {{ background: #f1f3f5; border-bottom: 1px solid #6c757d; padding: 28px min(6vw, 56px); }}
    main {{ max-width: 1180px; margin: 0 auto; padding: 28px min(5vw, 44px) 64px; }}
    h1 {{ margin: 0 0 8px; font-size: 32px; letter-spacing: 0; }}
    table {{ width: 100%; border-collapse: collapse; margin-top: 20px; }}
    th, td {{ border: 1px solid #d6dadd; padding: 8px 10px; vertical-align: top; overflow-wrap: anywhere; }}
    th {{ background: #e9ecef; text-align: left; }}
    tr:nth-child(even) td {{ background: #fafafa; }}
    code {{ background: #e9ecef; border: 1px solid #cfd4d8; border-radius: 4px; padding: 1px 5px; }}
    a {{ color: #2f4f6f; }}
  </style>
</head>
<body>
  <header>
    <h1>PX4 Study Docs</h1>
    <p>Generated architecture study documents for <code>src/modules</code>.</p>
    <p>Targets: <strong>{len(infos)}</strong>. Scope: all immediate <code>src/modules/*</code> directories plus nested directories that declare <code>px4_add_module(...)</code>.</p>
  </header>
  <main>
    <table>
      <thead><tr><th>Module</th><th>Build kind</th><th>Target</th><th>Topics</th><th>Classes</th></tr></thead>
      <tbody>{''.join(html_rows)}</tbody>
    </table>
  </main>
</body>
</html>
"""
    (OUT_ROOT / "index.html").write_text(index_html, encoding="utf-8")


def main() -> None:
    MODULE_OUT.mkdir(parents=True, exist_ok=True)
    module_paths = find_module_paths()
    infos = [module_info(path, index, module_paths) for index, path in enumerate(module_paths)]
    for info in infos:
        write_markdown(info)
        write_html(info)
    write_index(infos)
    print(f"Generated {len(infos)} module docs in {OUT_ROOT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
