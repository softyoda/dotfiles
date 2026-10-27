import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from dotctl import core

class SyncTests(unittest.TestCase):
    def test_private_directory_is_not_pulled_even_inside_parent_repo(self):
        with tempfile.TemporaryDirectory() as d:
            public = Path(d)
            subprocess.run(['git', 'init', '-q', d], check=True)
            private = public / 'private'
            private.mkdir()
            self.assertTrue(core.is_git_root(public))
            self.assertFalse(core.is_git_root(private))
            with patch.object(core, 'DOTFILES', public), patch.object(core, 'private_dir', return_value=private):
                self.assertEqual(core.repos(), [public])
                real_git = core.git
                pulls = []
                def git(repo, *args):
                    if args[0] == 'pull':
                        pulls.append(repo)
                        return subprocess.CompletedProcess(args, 0, 'Already up to date.', '')
                    return real_git(repo, *args)
                logs = []
                with patch.object(core, 'git', side_effect=git):
                    self.assertTrue(core.sync(logs.append))
                self.assertEqual(pulls, [public])
                self.assertIn('ne vérifie pas', logs[-1])

    def test_git_private_is_included_and_pull_failure_propagates(self):
        with tempfile.TemporaryDirectory() as d:
            public, private = Path(d)/'public', Path(d)/'private'
            for p in (public, private):
                subprocess.run(['git', 'init', '-q', str(p)], check=True)
            with patch.object(core, 'DOTFILES', public), patch.object(core, 'private_dir', return_value=private):
                self.assertEqual(core.repos(), [public, private])
                self.assertFalse(core.sync(lambda *_: None))
