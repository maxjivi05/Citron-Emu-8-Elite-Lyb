<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Citron-Emu (Android 8 Elite / Lyb Fork)</title>
    <!-- Load Tailwind CSS -->
    <script src="https://cdn.tailwindcss.com"></script>
    <!-- Load Inter font -->
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;700&display=swap" rel="stylesheet">
    <style>
        /* Apply Inter font */
        body {
            font-family: 'Inter', sans-serif;
        }
        /* Style for the blockquote */
        blockquote {
            border-left: 4px solid #4a5568; /* gray-700 */
            padding-left: 1rem;
            color: #a0aec0; /* gray-400 */
            font-style: italic;
        }
    </style>
</head>
<body class="bg-gray-900 text-gray-200 min-h-screen antialiased">

    <!-- Main Content Container -->
    <main class="max-w-3xl mx-auto p-6 md:p-10">
        
        <!-- Header -->
        <h1 class="text-3xl md:text-4xl font-bold text-white mb-4">
            Citron-Emu (Android 8 Elite / Lyb Fork)
        </h1>

        <!-- Note Block -->
        <blockquote class="bg-gray-800 border-gray-700 p-4 rounded-lg my-6">
            <strong>Note:</strong> This is a specialized fork of 
            <a href="https://citron-emu.org" class="text-blue-400 hover:underline">Citron-Emu</a> 
            focused on providing patched Android builds. For the official project, please see the links at the bottom of this file.
        </blockquote>

        <!-- Main Description -->
        <p class="text-lg text-gray-300 mb-6">
            This repository automatically builds the Android version of Citron and applies custom patches to enhance performance and stability on specific devices.
        </p>

        <!-- Divider -->
        <hr class="border-gray-700 my-8">

        <!-- Patches Section -->
        <section>
            <h3 class="text-2xl font-bold text-white mb-4">
                Applied Patches & Fixes
            </h3>
            <p class="text-gray-300 mb-4">
                This build is configured specifically for <strong>Android</strong> and includes the following modifications:
            </p>
            <ul class="list-disc list-inside space-y-2 text-gray-300 mb-6">
                <li><strong>Snapdragon 8 Elite Optimization:</strong> Includes fixes for the Snapdragon 8 Elite SoC.</li>
                <li><strong>Lyb Frame Generation:</strong> The build is configured to support Lyb Frame Generation.</li>
                <li><strong>Vulkan Stability Patches:</strong> Applies patches to disable known-broken Vulkan extensions on Qualcomm Adreno drivers (such as <code>shaderInt64</code> and <code>shader_atomic_int64</code>) to prevent driver instability and crashes.</li>
            </ul>
            <p class="text-gray-300">
                Builds are triggered automatically by the GitHub Actions in this repository.
            </p>
        </section>

        <!-- Community Section -->
        <section class="my-8">
            <h3 class="text-2xl font-bold text-white mb-4">
                Community
            </h3>
            <a href="https://discord.gg/jM2z3B2XNv" 
               class="inline-flex items-center bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-5 rounded-lg transition-colors duration-200">
                <!-- Discord Logo SVG -->
                <svg class="w-6 h-6 mr-3" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true">
                    <path d="M20.222 0H3.778C1.691 0 0 1.691 0 3.778v16.444C0 22.309 1.691 24 3.778 24h16.444C22.309 24 24 22.309 24 20.222V3.778C24 1.691 22.309 0 20.222 0zM8.333 18.2c-1.46 0-2.653-1.194-2.653-2.653s1.194-2.653 2.653-2.653c1.46 0 2.653 1.194 2.653 2.653S9.794 18.2 8.333 18.2zm7.334 0c-1.46 0-2.653-1.194-2.653-2.653s1.194-2.653 2.653-2.653c1.46 0 2.653 1.194 2.653 2.653S17.127 18.2 15.667 18.2zm-6.2-7.583c-1.018.01-2.008.384-2.73 1.053-.18.167-.46.134-.604-.07C6 11.458 5.798 11.2 5.75 10.93c-.07-.39.213-.75.597-.75h11.306c.383 0 .666.36.597.75-.048.27-.25.528-.393.673-.145.204-.425.237-.605.07-.723-.67-1.713-1.043-2.73-1.053h-.068c-.628-.6-1.408-.96-2.228-.96s-1.6.36-2.228.96h-.068z"/>
                </svg>
                Join our Discord Community
            </a>
        </section>

        <!-- Divider -->
        <hr class="border-gray-700 my-8">

        <!-- Footer -->
        <footer class="text-center text-gray-400">
            <p>Made with 💚 by <strong>Zephyron</strong> | 
                <a href="https://git.citron-emu.org" class="text-blue-400 hover:underline">Official Source Code</a>
            </p>
        </footer>

    </main>

</body>
</html>

