#version 330 core

in vec3 position;
in vec3 normal;

out vec3 normal_worldspace;
out vec3 normal_eyespace;
out vec3 vertex_direction_eyespace;
out vec3 lightdirection_eyespace;

uniform mat4 mvp;
uniform mat4 model;
uniform mat4 view;

void main() {
    gl_Position = mvp * vec4(position, 1.0);

    vec3 lightpos = vec3(0.0, -100.0, 0.0);

    vec3 position_eyespace = (view * model * vec4(position, 1.0)).xyz;
    vertex_direction_eyespace = vec3(0.0, 0.0, 0.0) - position_eyespace;

    vec3 position_worldspace = (model * vec4(position, 1.0)).xyz;
    vec3 light_direction_worldspace = lightpos - position_worldspace;
    lightdirection_eyespace = (view * vec4(light_direction_worldspace, 0.0)).xyz;

    normal_worldspace = (transpose(inverse(model)) * vec4(normal, 0.0)).xyz;
    normal_eyespace = (transpose(inverse(view * model)) * vec4(normal, 0.0)).xyz;
}
