# A part of NonVisual Desktop Access (NVDA)
# Copyright (C) 2026 NV Access Limited, Andrew Johnson
# This file may be used under the terms of the GNU General Public License, version 2 or later, as modified by the NVDA license.
# For full terms and any additional permissions, see the NVDA license file: https://github.com/nvaccess/nvda/blob/master/copying.txt

"""Unit tests for cancelling settings dialogs when the configuration is reset."""

import unittest

import wx
from gui.settingsDialogs import SettingsDialog


class _RecordingDialog(SettingsDialog):
	cancelled: list[str]

	def makeSettings(self, sizer):
		pass

	def onCancel(self, evt):
		self.cancelled.append(self.title)
		super().onCancel(evt)


class _ConfigDialog(_RecordingDialog):
	title = "config"


class _ChildConfigDialog(_RecordingDialog):
	title = "child"


class _NonConfigDialog(_RecordingDialog):
	title = "nonConfig"
	shouldSuspendConfigProfileTriggers = False


class Test_cancelConfigDialogs(unittest.TestCase):
	def setUp(self):
		self.app = wx.App()
		self.cancelled = []
		self.dialogs = []

	def tearDown(self):
		for dialog in self.dialogs:
			if dialog:
				dialog.Destroy()
		self.app.Destroy()

	def _open(self, cls, parent=None):
		dialog = cls(parent, multiInstanceAllowed=True)
		dialog.cancelled = self.cancelled
		self.dialogs.append(dialog)
		return dialog

	def test_cancelsConfigDialogsLatestFirst(self):
		"""A dialog opened from the settings dialog is cancelled before the settings dialog (#6469)."""
		parent = self._open(_ConfigDialog)
		self._open(_ChildConfigDialog, parent)
		SettingsDialog._cancelConfigDialogs()
		self.assertEqual(self.cancelled, ["child", "config"])

	def test_leavesOtherDialogsOpen(self):
		"""Dialogs that don't edit the configuration, such as the Add-on Store, stay open."""
		self._open(_NonConfigDialog)
		SettingsDialog._cancelConfigDialogs()
		self.assertEqual(self.cancelled, [])
