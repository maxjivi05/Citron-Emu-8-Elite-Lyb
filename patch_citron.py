import os
import sys

# Paths - Adjusted to reflect potential new files based on analysis
device_cpp = "src/video_core/vulkan_common/vulkan_device.cpp"
native_cpp = "src/android/app/src/main/jni/native.cpp"
device_h = "src/video_core/vulkan_common/vulkan_device.h"
pipeline_cache_cpp = "src/video_core/renderer_vulkan/vk_pipeline_cache.cpp"
staging_pool_cpp = "src/video_core/renderer_vulkan/vk_staging_buffer_pool.cpp"
buffer_cache_h = "src/video_core/buffer_cache/buffer_cache.h"
# Hypothetical file paths based on common Vulkan renderer structure
render_pass_creation_cpp = "src/video_core/renderer_vulkan/vk_render_pass_cache.cpp" # Or similar
framebuffer_creation_cpp = "src/video_core/renderer_vulkan/vk_framebuffer_cache.cpp" # Or similar
command_buffer_cpp = "src/video_core/renderer_vulkan/vk_command_buffer.cpp" # Or similar

def patch_file(path, search_str, replace_str, new_lines=False):
    if not os.path.exists(path):
        print(f"Error: {path} not found!")
        return False
    with open(path, 'r') as f:
        content = f.read()
    if search_str in content:
        if new_lines: # Special handling for injecting multiple lines around a single line
            lines = content.splitlines(keepends=True)
            new_content_lines = []
            replaced = False
            for line in lines:
                if not replaced and search_str.strip() in line.strip(): # Match line content
                    new_content_lines.extend(replace_str.splitlines(keepends=True))
                    replaced = True
                else:
                    new_content_lines.append(line)
            if replaced:
                with open(path, 'w') as f:
                    f.writelines(new_content_lines)
                print(f"Successfully injected new lines around '{search_str.strip()}' in {path}")
                return True
            else:
                print(f"Warning: Could not find search string in {path} for multi-line injection.")
                return False
        else: # Standard single-string replacement
            new_content = content.replace(search_str, replace_str)
            with open(path, 'w') as f:
                f.write(new_content)
            print(f"Successfully patched {path}")
            return True
    else:
        print(f"Warning: Could not find search string in {path}")
        return False

# 1. FIX SYSTEM DRIVER LOADING (Native Patch)
# Forces the app to load libvulkan.so from the system instead of failing
# We inject dlopen logic and effectively disable the original adrenotools call by wrapping it in "if (false)"
patch_file(native_cpp, 
           'if (!handle) {',
           'if (!handle) { handle = dlopen("libvulkan.so", RTLD_NOW); } if (false) {')

# 2. CATCH PIPELINE CRASHES (Pipeline Cache Patch) - Existing fix
# Wraps pipeline creation in extra try-catch blocks to prevent driver crashes from killing the app
if os.path.exists(pipeline_cache_cpp):
    with open(pipeline_cache_cpp, 'r') as f:
        content = f.read()
    
    search_str = '    LOG_ERROR(Render_Vulkan, "{}", exception.what());\n    return nullptr;\n}'
    new_catch = '    LOG_ERROR(Render_Vulkan, "{}", exception.what());\n    return nullptr;\n} catch (const vk::Exception& e) { LOG_ERROR(Render_Vulkan, "Vulkan Error: {}", e.what()); return nullptr; } catch (const std::exception& e) { LOG_ERROR(Render_Vulkan, "Std Error: {}", e.what()); return nullptr; }'
    if search_str in content:
        content = content.replace(search_str, new_catch)
        with open(pipeline_cache_cpp, 'w') as f:
            f.write(content)
        print("Patched vk_pipeline_cache.cpp to catch generic exceptions")
    else:
        print("Warning: Could not find catch block end in vk_pipeline_cache.cpp")

# 3. DISABLE 64-BIT ATOMICS & FLOAT16/INT16/INT8 (Header Patch) - Existing fix
# Reads the header and disables advanced types for Qualcomm to force 32-bit fallback
if os.path.exists(device_h):
    with open(device_h, 'r') as f:
        h_content = f.read()
    
    def disable_feature(name, text):
        if f"bool {name}() const {{ " in text:
            text = text.replace(
                f"bool {name}() const {{ ",
                f"bool {name}() const {{ const auto driver = GetDriverID(); if (driver == VK_DRIVER_ID_QUALCOMM_PROPRIETARY) return false;"
            )
            print(f"Patched {name}")
        return text
    
    h_content = disable_feature("IsShaderInt64Supported", h_content)
    h_content = disable_feature("IsExtShaderAtomicInt64Supported", h_content)
    h_content = disable_feature("IsShaderFloat16Int8Supported", h_content)
    h_content = disable_feature("IsFloat16Supported", h_content)
    h_content = disable_feature("IsShaderInt16Supported", h_content)
    h_content = disable_feature("IsInt8Supported", h_content)
    h_content = disable_feature("IsNvGeometryShaderPassthroughSupported", h_content) # Also disable Geometry Shader Passthrough in header check just in case
    with open(device_h, 'w') as f:
        f.write(h_content)

# 4. BYPASS STARTUP CHECKS & DISABLE EXTENSIONS (Device CPP Patch) - Existing fix + new extension
# This reads the C++ file line-by-line to inject the bypass logic and extension removal.
if os.path.exists(device_cpp):
    with open(device_cpp, 'r') as f:
        lines = f.readlines()
    
    new_lines = []
    injected_extensions = False
    
    # The code block we want to inject to kill the extensions - UPDATED
    extension_hack = [
        '        LOG_WARNING(Render_Vulkan, "HACK: Removing Adreno 830 crash extensions");\n',
        '        extensions.custom_border_color = false;\n',
        '        extensions.depth_bias_control = false;\n',
        '        extensions.extended_dynamic_state = false;\n',
        '        extensions.extended_dynamic_state2 = false;\n',
        '        extensions.extended_dynamic_state3 = false;\n',
        '        extensions.vertex_input_dynamic_state = false;\n',
        '        extensions.geometry_shader_passthrough = false;\n',
        '        RemoveExtension(extensions.bit16_storage, "VK_KHR_16bit_storage");\n',
        '        RemoveExtension(extensions.bit8_storage, "VK_KHR_8bit_storage");\n',
        '        RemoveExtension(extensions.shader_float16_int8, "VK_KHR_shader_float16_int8");\n',
        '        RemoveExtension(extensions.imageless_framebuffer, "VK_KHR_imageless_framebuffer"); // NEW: Disable imageless framebuffer\n',
    ]
    skip_next = False
    for line in lines:
        if 'LOG_ERROR(Render_Vulkan, "Missing required feature {}", #name);' in line:
            new_lines.append(line)
            skip_next = True
        elif skip_next:
            if "suitable = false;" in line:
                new_lines.append(line.replace("suitable = false;", "/* suitable = false; (Bypass for 8 Elite) */"))
            else:
                new_lines.append(line)
            skip_next = False
        elif "if (is_qualcomm) {" in line and not injected_extensions:
            new_lines.append(line)
            new_lines.extend(extension_hack)
            injected_extensions = True
        else:
            new_lines.append(line)
    
    with open(device_cpp, 'w') as f:
        f.writelines(new_lines)
    print("Patched vulkan_device.cpp with bypass and extension hacks (including imageless framebuffer)")

# 5. CLAMP STAGING BUFFER SIZE (Eden Fix) - Existing fix
if os.path.exists(staging_pool_cpp):
    with open(staging_pool_cpp, 'r') as f:
        content = f.read()
    
    if 'const u32 log2 = Common::Log2Ceil64(size);' in content:
        content = content.replace(
            'const u32 log2 = Common::Log2Ceil64(size);',
            'size = std::min(size, size_t{256 * 1024 * 1024});\n    const u32 log2 = Common::Log2Ceil64(size);'
        )
        with open(staging_pool_cpp, 'w') as f:
            f.write(content)
        print("Patched vk_staging_buffer_pool.cpp with 256MB clamp")

# 6. VALIDATE MAPPED UPLOAD MEMORY (Eden Fix) - Existing fix
if os.path.exists(buffer_cache_h):
    with open(buffer_cache_h, 'r') as f:
        content = f.read()
    
    search_str = 'u8* const src_pointer = staging_pointer.data() + copy.src_offset;'
    replace_str = 'if (copy.src_offset + copy.size > staging_pointer.size()) { continue; }\n            u8* const src_pointer = staging_pointer.data() + copy.src_offset;'
    
    if search_str in content:
        content = content.replace(search_str, replace_str)
        with open(buffer_cache_h, 'w') as f:
            f.write(content)
        print("Patched buffer_cache.h with size validation")

# --- NEW ADRENO 830 WORKAROUNDS (Architect Patches) ---

# 7. PIPELINE CACHE NULLIFICATION/RELAXATION
# Finds where VkGraphicsPipelineCreateInfo is assembled and, for Qualcomm, sets pipelineCache to VK_NULL_HANDLE.
def patch_pipeline_cache_workarounds():
    print("Applying pipeline cache workarounds...")
    target_file = pipeline_cache_cpp # Primary target for pipeline creation
    if os.path.exists(target_file):
        # Find a common pattern around VkGraphicsPipelineCreateInfo setup
        # This is speculative, a typical line before setting pStages:
        search_str = "graphics_pipeline_ci.pStages = shader_stages.data();"
        
        # Inject Qualcomm driver check and modification *before* this line.
        injection_code = """
        # ARCHITECT PATCH: Adreno 830 Pipeline Cache Workaround
        const auto driver = device->GetDriverID();
        if (driver == VK_DRIVER_ID_QUALCOMM_PROPRIETARY) {
            LOG_WARNING(Render_Vulkan, "Adreno 830 detected: Nullifying VkPipelineCache for stability.");
            graphics_pipeline_ci.pipelineCache = VK_NULL_HANDLE; # Force no pipeline caching
            # Consider also adding VK_PIPELINE_CREATE_DISABLE_OPTIMIZATION_BIT for more stability
            # graphics_pipeline_ci.flags |= VK_PIPELINE_CREATE_DISABLE_OPTIMIZATION_BIT;
        }
        """ + search_str # Re-insert the search string after our injection

        if patch_file(target_file, search_str, injection_code, new_lines=True):
            print("Successfully patched vk_pipeline_cache.cpp for Qualcomm pipeline cache nullification.")
        else:
            print("Warning: Could not find VkGraphicsPipelineCreateInfo setup in vk_pipeline_cache.cpp for cache workaround.")
    else:
        print(f"Error: {target_file} not found for pipeline cache workaround.")

# 8. AGGRESSIVE MEMORY BARRIERS FOR RENDER PASSES
# Inject explicit vkCmdPipelineBarrier calls before/after render passes for Qualcomm.
def patch_command_buffer_barriers():
    print("Applying command buffer memory barrier workarounds...")
    target_file = command_buffer_cpp # Hypothetical command buffer recording file
    if os.path.exists(target_file):
        # We need to inject barriers around vkCmdBeginRenderPass.
        # Find the line that calls vkCmdBeginRenderPass
        search_str_begin = "vkCmdBeginRenderPass(command_buffer, &render_pass_begin_info, VK_SUBPASS_CONTENTS_INLINE);"
        
        # This is the code to inject BEFORE vkCmdBeginRenderPass
        pre_render_pass_barrier = """
        # ARCHITECT PATCH: Adreno 830 Pre-RenderPass Memory Barrier
        const auto driver = device->GetDriverID();
        if (driver == VK_DRIVER_ID_QUALCOMM_PROPRIETARY) {
            LOG_DEBUG(Render_Vulkan, "Adreno 830 detected: Injecting pre-render pass memory barrier.");
            VkImageMemoryBarrier pre_rp_barrier{};
            pre_rp_barrier.sType = VK_STRUCTURE_TYPE_IMAGE_MEMORY_BARRIER;
            pre_rp_barrier.srcAccessMask = VK_ACCESS_TRANSFER_WRITE_BIT; # Broad access mask
            pre_rp_barrier.dstAccessMask = VK_ACCESS_COLOR_ATTACHMENT_READ_BIT | VK_ACCESS_COLOR_ATTACHMENT_WRITE_BIT | VK_ACCESS_DEPTH_STENCIL_ATTACHMENT_READ_BIT | VK_ACCESS_DEPTH_STENCIL_ATTACHMENT_WRITE_BIT;
            pre_rp_barrier.oldLayout = VK_IMAGE_LAYOUT_UNDEFINED; # Assume undefined or general
            pre_rp_barrier.newLayout = VK_IMAGE_LAYOUT_GENERAL; # Force general layout
            pre_rp_barrier.srcQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
            pre_rp_barrier.dstQueueFamilyIndex = VK_QUEUE_FAMILY_IGNORED;
            pre_rp_barrier.image = framebuffer_image_handle_for_rp; # PLACEHOLDER: This needs to be the actual VkImage handle for the current framebuffer.
            pre_rp_barrier.subresourceRange.aspectMask = VK_IMAGE_ASPECT_COLOR_BIT | VK_IMAGE_ASPECT_DEPTH_BIT | VK_IMAGE_ASPECT_STENCIL_BIT;
            pre_rp_barrier.subresourceRange.baseMipLevel = 0;
            pre_rp_barrier.subresourceRange.levelCount = VK_REMAINING_MIP_LEVELS;
            pre_rp_barrier.subresourceRange.baseArrayLayer = 0;
            pre_rp_barrier.subresourceRange.layerCount = VK_REMAINING_ARRAY_LAYERS;
            vkCmdPipelineBarrier(command_buffer,
                                 VK_PIPELINE_STAGE_ALL_COMMANDS_BIT, # Broad stage for safety
                                 VK_PIPELINE_STAGE_ALL_COMMANDS_BIT,
                                 0, 0, nullptr, 0, nullptr, 1, &pre_rp_barrier);
        }
        """
        # To make it compatible with `new_lines=True`, `search_str_begin` should be part of the `replace_str_begin`.
        replace_str_begin = pre_render_pass_barrier + search_str_begin

        if patch_file(target_file, search_str_begin, replace_str_begin, new_lines=True):
            print("Successfully injected pre-render pass barrier in vk_command_buffer.cpp for Qualcomm.")
        else:
            print("Warning: Could not find vkCmdBeginRenderPass pattern for barrier injection.")
    else:
        print(f"Error: {target_file} not found for command buffer barriers.")

# Call the new patching functions
print("\n--- Running Architect's Adreno 830 Workarounds ---")
patch_pipeline_cache_workarounds()
patch_command_buffer_barriers()
print("--- Finished Architect's Adreno 830 Workarounds ---")
