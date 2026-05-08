#version 330 core

in vec3 position;
in vec3 normal;

out vec2 TexCoords;

uniform mat4 mvp;

void main() {
    // output position of the vertex
    gl_Position = mvp * vec4(position, 1.0);
    TexCoords = vec2((position.x + 1) / 2, -(position.y - 1) / 2);  // [-1..1] -> [0..±1]
}
