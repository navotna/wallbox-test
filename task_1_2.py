"""A function that given a path of the file system finds the first file that meets the
following requirements
a. The file owner is admin
b. The file is executable
c. The file has a size lower than 14*2^20
"""
import os
import pwd
import shutil
import stat
import tempfile
import unittest
from contextlib import contextmanager
from pathlib import Path
from typing import Union, Optional, Tuple, Dict, List


def find_file(
    target_path: Union[str, Path],
    owner: str = "admin",
    permissions: int = stat.S_IXGRP | stat.S_IXOTH | stat.S_IXUSR,
    max_size: int = 14 * 2 ** 20 - 1,
) -> Optional[Path]:
    """
    :param target_path: folder to search file for

    Finds recursively in folder the first (any of) file satisfying the following criteria

    :param owner: username of file owner
    :param permissions: permission mask
    :param max_size: max size of the file
    :return: None if no such file, Path instance if found
    """
    for p in Path(target_path).rglob("*"):
        if (
            p.is_file()
            and p.owner() == owner
            and os.access(p, permissions)
            and p.stat().st_size <= max_size
        ):
            return p
    else:
        return None


class TestFindMyFile(unittest.TestCase):
    ok_user_uid = os.getuid()
    ok_user = pwd.getpwuid(ok_user_uid)[0]
    no_user = "nobody"

    @staticmethod
    @contextmanager
    def _generate_structure_and_mocked_owner(
        structure: Dict[str, List[Union[Dict, Tuple[str, str, int, int]]]]
    ) -> Path:
        """
        Creates temporary folder/file structure with passed definitions.
        Monkey-Patch of Path.owner to be able to test function without creating users
        """
        root = Path(tempfile.gettempdir()) / "find_my_file_test"
        root.mkdir()

        filepath_to_owner_map = {}

        def make_dir(dir_root, dir_structure):
            for dir_name, children in dir_structure.items():
                dir_path = Path(dir_root / dir_name)
                dir_path.mkdir()
                for child in children:
                    if isinstance(child, dict):
                        make_dir(dir_path, child)
                    elif isinstance(child, tuple):
                        name, owner_name, permissions, size = child
                        file_path = dir_path / name
                        with file_path.open("wb") as f:
                            f.seek(size - 1)
                            f.write(b"\0")
                        filepath_to_owner_map[file_path] = owner_name
                        os.chmod(file_path, permissions)
                    else:
                        raise ValueError(f"Not supported type: {type(child)}")

        make_dir(root, structure)

        Path._original_owner = Path.owner

        def fake_path_owner_method(path_instance):
            mocked_owner = filepath_to_owner_map.get(path_instance, None)
            if mocked_owner:
                return mocked_owner
            else:
                return path_instance._original_owner()

        Path.owner = fake_path_owner_method
        try:
            yield root
        finally:
            Path.owner = Path._original_owner
            shutil.rmtree(root)

    def test_find_my_file(self):
        for test_folder_structure, expected_paths in [
            # owner - OK, permissions - OK, size more than required
            # expecting None
            (
                {
                    "test_1": [
                        (
                            "file_userOk_permOk_sizeNo",
                            self.ok_user,
                            stat.S_IXUSR,
                            14 * 2 ** 20,
                        ),
                    ]
                },
                [],
            ),
            # owner - not correct, permissions - OK, size - OK
            # expecting None
            (
                {
                    "test_2": [
                        (
                            "file_userNo_permOk_sizeOk",
                            self.no_user,
                            stat.S_IXUSR,
                            14 * 2 ** 20 - 1,
                        ),
                    ]
                },
                [],
            ),
            # owner - OK, permissions - just read for group, size - OK
            # expecting None
            (
                {
                    "test_3": [
                        (
                            "file_userOk_permNo_sizeOk",
                            self.ok_user,
                            stat.S_IRGRP,
                            14 * 2 ** 20 - 1,
                        ),
                    ]
                },
                [],
            ),
            # Two files, one - OK, the second - not OK
            # expecting path of the OK file
            (
                {
                    "test_4": [
                        (
                            "file_userOk_permNo_sizeOk",
                            self.ok_user,
                            stat.S_IRGRP,
                            14 * 2 ** 20 - 1,
                        ),
                        (
                            "file_userOk_permOk_sizeOk",
                            self.ok_user,
                            stat.S_IXUSR,
                            14 * 2 ** 20 - 1,
                        ),
                    ]
                },
                ["test_4/file_userOk_permOk_sizeOk"],
            ),
            # Two files, one child of root folder and does not satisfy criteria,
            # the second - OK, but in the subfolder
            # expecting path of the OK file
            (
                {
                    "test_5": [
                        (
                            "file_userOk_permNo_sizeOk",
                            self.ok_user,
                            stat.S_IRGRP,
                            14 * 2 ** 20 - 1,
                        ),
                        {
                            "subfolder": [
                                (
                                    "file_userOk_permOk_sizeOk",
                                    self.ok_user,
                                    stat.S_IXUSR,
                                    14 * 2 ** 20 - 1,
                                )
                            ]
                        },
                    ]
                },
                ["test_5/subfolder/file_userOk_permOk_sizeOk"],
            ),
            # Two OK files
            # expecting any
            (
                {
                    "test_6": [
                        (
                            "file_userOk_permOk_sizeOk_1",
                            self.ok_user,
                            stat.S_IXUSR,
                            14 * 2 ** 20 - 1,
                        ),
                        (
                            "file_userOk_permOk_sizeOk_2",
                            self.ok_user,
                            stat.S_IXUSR,
                            14 * 2 ** 20 - 1,
                        ),
                    ]
                },
                [
                    "test_6/file_userOk_permOk_sizeOk_1",
                    "test_6/file_userOk_permOk_sizeOk_2",
                ],
            ),
        ]:
            with self.subTest(
                structure=test_folder_structure, expected_paths=expected_paths
            ):

                with self._generate_structure_and_mocked_owner(
                    test_folder_structure
                ) as target_folder:
                    expected_paths = [target_folder / each for each in expected_paths]
                    actual_filpath = find_file(target_folder, owner=self.ok_user)
                    if expected_paths:
                        self.assertIn(actual_filpath, expected_paths)
                    else:
                        self.assertIs(actual_filpath, None)
