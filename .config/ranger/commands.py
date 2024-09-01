import os
import json
from ranger.core.loader import CommandLoader, Popen, sleep
from ranger.api.commands import Command
from ranger.ext.signals import Signal

try:
    appsettings: dict[str, str] = json.loads(
        open(os.path.join(os.path.dirname(__file__), "appsettings.json")).read()
    )

    PHONE_IP = appsettings["ipAddress"]
    LOCATION_IN_PHONE = appsettings["defaultPath"]
except Exception as e:
    Command.fm.notify(str(e), bad=True)
    pass


class send_to_phone(Command):
    def execute(self):
        cwd = self.fm.thisdir
        marked_files_paths: list[str] = list(map(lambda x: x.path, cwd.get_selection()))

        self.fm.execute_command("mullvad disconnect")
        sleep(1)

        count_finished = 0
        for file in marked_files_paths:

            def on_finish(x: Signal):
                process: Popen = x["process"]
                if process.returncode == 0:
                    self.fm.notify(f"File {file} has been sent to {PHONE_IP}")

                nonlocal count_finished
                count_finished += 1

                if count_finished == len(marked_files_paths):
                    self.fm.execute_command("mullvad connect")

            command_args: list[str] = [
                "scp",
                "-P",
                "8022",
                file,
                f"{PHONE_IP}:{LOCATION_IN_PHONE}",
            ]
            commands_loader = CommandLoader(
                args=command_args, descr=f"Sending to {PHONE_IP} {file}"
            )
            commands_loader.signal_bind("after", on_finish)
            self.fm.loader.add(commands_loader)


class decompress(Command):
    def execute(self):
        """extract selected files to current directory."""
        cwd = self.fm.thisdir
        marked_files = tuple(cwd.get_selection())

        def refresh(_):
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        one_file = marked_files[0]
        cwd = self.fm.thisdir
        original_path = cwd.path
        au_flags = ["-x", cwd.path]
        au_flags += self.line.split()[1:]
        au_flags += ["-e"]

        self.fm.copy_buffer.clear()
        self.fm.cut_buffer = False
        if len(marked_files) == 1:
            descr = "extracting: " + os.path.basename(one_file.path)
        else:
            descr = "extracting files from: " + os.path.basename(one_file.dirname)
        obj = CommandLoader(
            args=["aunpack"] + au_flags + [f.path for f in marked_files],
            descr=descr,
            read=True,
        )

        obj.signal_bind("after", refresh)
        self.fm.loader.add(obj)


class compress(Command):
    def execute(self):
        """Compress marked files to current directory"""
        cwd = self.fm.thisdir
        marked_files = cwd.get_selection()

        if not marked_files:
            return

        def refresh(_):
            cwd = self.fm.get_directory(original_path)
            cwd.load_content()

        original_path = cwd.path
        parts = self.line.split()
        au_flags = parts[1:]

        descr = "compressing files in: " + os.path.basename(parts[1])
        obj = CommandLoader(
            args=["apack"]
            + au_flags
            + [os.path.relpath(f.path, cwd.path) for f in marked_files],
            descr=descr,
            read=True,
        )

        obj.signal_bind("after", refresh)
        self.fm.loader.add(obj)

    def tab(self, tabnum):
        """Complete with current folder name"""

        extension = [
            ".zip",
            ".tar.gz",
            ".rar",
            ".7z",
        ]
        return [
            "compress " + os.path.basename(self.fm.thisdir.path) + ext
            for ext in extension
        ]
