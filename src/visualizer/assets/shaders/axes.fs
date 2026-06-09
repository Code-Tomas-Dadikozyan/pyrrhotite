#version 330 core

in vec3 normal_worldspace;
in vec3 normal_eyespace;
in vec3 vertex_direction_eyespace;
in vec3 lightdirection_eyespace;

out vec4 fragColor;

uniform vec3 color;

float ambient_strength = 0.1;
float specular_strength = 0.5;

void main() {
    vec3 lightcolor = vec3(1.0, 1.0, 1.0);

    vec3 l = normalize(lightdirection_eyespace);
    vec3 n = normalize(normal_eyespace);
    vec3 e = normalize(vertex_direction_eyespace);
    vec3 r = reflect(-l, n);

    float cosTheta = clamp(dot(n, l), 0.0, 1.0);
    float cosAlpha = clamp(dot(e, r), 0.0, 1.0);

    vec3 ambient  = ambient_strength * lightcolor;
    vec3 diffuse  = cosTheta * lightcolor;
    vec3 specular = pow(cosAlpha, 32.0) * specular_strength * lightcolor;

    fragColor = vec4((ambient + diffuse + specular) * color, 1.0);
}
