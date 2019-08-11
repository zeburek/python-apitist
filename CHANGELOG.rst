=========
Changelog
=========

Version 0.0.4
=============

- Add constructor to work with attrs classes
  (uses cattrs)
- Add default hooks to work with constructor:
    - RequestConverterHook
    - ResponseConverterHook

Version 0.0.3
=============

- Add default hooks:
    - RequestDebugLoggingHook
    - RequestInfoLoggingHook
    - PrepRequestDebugLoggingHook
    - PrepRequestInfoLoggingHook
    - ResponseDebugLoggingHook
    - ResponseInfoLoggingHook

Version 0.0.1-alpha
===================

- First project release
- Added custom Session implementation with custom hooks:
    - RequestHook
    - PreparedRequestHook
    - ResponseHook
