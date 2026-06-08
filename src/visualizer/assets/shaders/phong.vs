#version 330 core

layout(location = 0) in vec3 position;
layout(location = 1) in vec3 normal;

out vec3 vertex_direction_eyespace;
out vec3 lightdirection_eyespace;

out vec3 normal_worldspace;
out vec3 normal_eyespace;

uniform mat4 model;
uniform mat4 view;
uniform mat4 mvp;
uniform vec3 lightpos;
uniform vec3 object_color;

void main() {
    // output position of the vertex
    gl_Position = mvp * vec4(position, 1.0);

    // calculate vertex-to-camera direction in eye space
    vec3 position_eyespace = (view * model * vec4(position, 1.0)).xyz;
    vertex_direction_eyespace = vec3(0,0,0) - position_eyespace;

    // lightpos is in eye space — light follows the camera regardless of rotation
    lightdirection_eyespace = lightpos - position_eyespace;

    // vertex normals in world and eye space
    normal_worldspace = (transpose(inverse(model)) * vec4(normal, 0.0)).xyz;
    normal_eyespace = (transpose(inverse(view * model)) * vec4(normal, 0.0)).xyz;
}
