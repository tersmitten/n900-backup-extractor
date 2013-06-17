# -*- coding: utf-8 -*-

import sys

def show_usage(message):
  """
  Shows an usage message and exits.

  @param message: A usage message
  @type message: string
  """

  _show('Usage', message)

def show_error(message):
  """
  Shows an error message.

  @param message: An error message and exits.
  @type message: string
  """

  _show('Error', message)

def _show(title, message):
  """
  Shows a message and exits.

  @param title: A title
  @type title: string
  @param message: A message
  @type message: string
  """

  print
  print '%s:' % title
  print '  %s' % message
  print
  sys.exit(1)
