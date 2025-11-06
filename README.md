Citron-Emu (Android 8 Elite / Lyb Fork)

Note: This is a specialized fork of Citron-Emu focused on providing patched Android builds. For the official project, please see the links at the bottom of this file.

This repository automatically builds the Android version of Citron and applies custom patches to enhance performance and stability on specific devices.

Applied Patches & Fixes
This build is configured specifically for Android and includes the following modifications:

* Snapdragon 8 Elite Optimization: Includes fixes for the Snapdragon 8 Elite SoC.
* Lyb Frame Generation: The build is configured to support Lyb Frame Generation.
* Vulkan Stability Patches: Applies patches to disable known-broken Vulkan extensions on Qualcomm Adreno drivers (such as shaderInt64 and shader_atomic_int64) to prevent driver instability and crashes.

Builds are triggered automatically by the GitHub Actions in this repository.

Community
Join our Discord Community
https://discord.gg/jM2z3B2XNv
