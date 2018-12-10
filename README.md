# swift_po aka `spo`

Substitute `po` command for Swift, with fewer corner cases to watch out for.

### Avoids Leaks

There's a bug in lldb that creates strong references to any object printed with `po`. The result is leaked objects, and missing calls to `deinit`.

```
(lldb) po self
```

After running this, `self` will never be released. This is not specific to `self`, it happens to any object. This is also true when using `expression`.

There are two work arounds:

1. `frame variable -O -- self`
2. `call print(self)`

These are what `swift_po` does for you. If the input can be resolved as a variable, then `frame variable ...` is used, otherwise it performs `call print(...)`.

### Object Pointers

From Swift, `po 0x76543210` will not work. This does work from objc though. `swift_po` works with memory addresses too, same as objc.

### Installation

First clone `swift_po`:

```sh
git clone https://github.com/kastiglione/swift_po.git
```

Next, edit your `~/.lldbinit` to `import` the `spo` command:

```
command script import path/to/swift_po/spo.py
```

### Usage

Call `spo` anywhere you'd normally call `po`.

If you would like to override `po` to be `spo`, add these to your `~/.lldbinit`:

```
command unalias po
command alias po spo
```

### What `swift_po` is doing

A summary of what `swift_po` does for you.


| `spo` command | equivalent lldb |
| - | - |
| `spo 0x76543210` | `expression -l objc -O -- 0x76543210` |
| `spo self` | `frame variable -O self` |
| `spo self.objects` | `frame variable -O self.objects` |
| `spo self.view` | `expression print(self.view)` |
| `spo some.function()` | `expression print(some.function())` |

This table show that some properties cannot be accessed using `frame variable`, in those cases `print()` is used instead.
