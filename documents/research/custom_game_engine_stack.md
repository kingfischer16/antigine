# Custom Game Engine Stack - C++ Libraries

## Core Framework
### SDL2
- **Purpose**: Window management, input handling, basic graphics context
- **Usage**: Create game window, handle events, manage OpenGL context
- **Installation**: Available on most package managers, cross-platform
- **Key Features**: Keyboard/mouse/gamepad input, audio device management

## Graphics & Rendering
### OpenGL 3.3+
- **Purpose**: 3D graphics rendering API
- **Usage**: Vertex buffers, shaders, textures, frame buffers
- **Target Version**: OpenGL 3.3 Core Profile (best compatibility)
- **Steam Deck**: Excellent support via Proton/Linux

### GLAD
- **Purpose**: OpenGL extension loader
- **Usage**: Load OpenGL function pointers at runtime
- **Alternative**: GLEW (older, more established)
- **Setup**: Generate loader from glad.dav1d.de

### GLM
- **Purpose**: Mathematics library for graphics
- **Usage**: Vectors, matrices, transformations, camera math
- **Features**: Header-only, OpenGL-compatible types
- **Key Types**: `glm::vec3`, `glm::mat4`, `glm::quat`

## Audio
### OpenAL
- **Purpose**: 3D positional audio
- **Usage**: Sound effects, music, spatial audio
- **Features**: Hardware acceleration, multiple sound sources
- **Formats**: Use with audio loading library

### libsndfile (Optional)
- **Purpose**: Audio file loading
- **Usage**: Load WAV, OGG, FLAC files for OpenAL
- **Alternative**: SDL2_mixer for simpler audio needs

## Asset Loading
### stb_image
- **Purpose**: Image/texture loading
- **Usage**: Load PNG, JPG, TGA for OpenGL textures
- **Benefits**: Single header file, no dependencies
- **Integration**: Perfect for texture loading pipeline

### tinyobjloader
- **Purpose**: OBJ model loading
- **Usage**: Load Blender-exported OBJ files with materials
- **Features**: Header-only, handles MTL files
- **Perfect for**: Your Blender workflow

## Physics
### Bullet Physics
- **Purpose**: 3D physics simulation
- **Usage**: Collision detection, rigid body dynamics, constraints
- **Components**: 
  - Collision detection (btCollisionWorld)
  - Dynamics (btDiscreteDynamicsWorld)
  - Shapes (btBoxShape, btSphereShape, btTriangleMesh)
- **Integration**: Step physics each frame, sync with rendering

## Build System
### CMake
- **Purpose**: Cross-platform build configuration
- **Usage**: Manage dependencies, compile flags
- **Benefits**: Works with Visual Studio, Make, Ninja
- **Package Managers**: vcpkg or Conan for dependency management

## Development Tools
### Dear ImGui (Optional)
- **Purpose**: Immediate mode GUI for debug tools
- **Usage**: Debug overlays, level editors, performance metrics
- **Integration**: Renders using your OpenGL context

## Recommended Architecture

### Engine Structure
```
Engine/
├── Core/           # Main loop, time management
├── Graphics/       # OpenGL wrapper, renderer
├── Audio/          # OpenAL wrapper
├── Input/          # SDL2 input handling
├── Physics/        # Bullet Physics integration
├── Assets/         # Resource loading and management
└── Math/           # GLM utilities and game-specific math
```

### Key Integration Points
- **Main Loop**: SDL2 event handling + OpenGL rendering + Bullet stepping
- **Asset Pipeline**: Load OBJ → Create OpenGL buffers → Register physics shapes
- **Transform System**: GLM matrices for rendering, Bullet transforms for physics
- **Input System**: SDL2 events → Game actions → Physics/rendering updates

## Performance Considerations
- **Batch Rendering**: Group draw calls by material/texture
- **LOD System**: Multiple detail levels for distance-based optimization
- **Culling**: Frustum and occlusion culling for 3D scenes
- **Memory Management**: Object pools for frequently created/destroyed objects
- **Profile Early**: Built-in timing for identifying bottlenecks

## Platform Notes
- **Steam Deck**: All libraries have excellent Linux compatibility
- **Low-end PCs**: OpenGL 3.3 runs on hardware from 2010+
- **Distribution**: Static linking recommended for simpler deployment