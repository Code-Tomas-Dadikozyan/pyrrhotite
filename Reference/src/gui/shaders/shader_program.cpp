/**
 * Schoenflies
 * Copyright (c) 2021 Luuk Kempen
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. If not, see <https://www.gnu.org/licenses/>.
 */

#include "shader_program.h"

/**
 * @brief Construct a new Shader Program object
 *
 * @param name shader program name
 * @param type shader program type
 * @param vertex_filename filename of vertex shader
 * @param fragment_filename filename of fragment shader
 */
ShaderProgram::ShaderProgram(const std::string& name, const ShaderProgramType type, const QString& vertex_filename, const QString& fragment_filename) {
    this->m_program = new QOpenGLShaderProgram;

    if (!this->m_program->addShaderFromSourceFile(QOpenGLShader::ShaderTypeBit::Vertex, vertex_filename)) {
        throw std::runtime_error("Could not add vertex shader: " + this->m_program->log().toStdString());
    }

    if (!this->m_program->addShaderFromSourceFile(QOpenGLShader::ShaderTypeBit::Fragment, fragment_filename)) {
        throw std::runtime_error("Could not add fragment shader: " + this->m_program->log().toStdString());
    }

    this->add_attributes(type);

    if (!this->m_program->link()) {
        throw std::runtime_error("Could not link shader: " + this->m_program->log().toStdString());
    }

    this->add_uniforms(type);
}

/**
 * @brief Destroy the Shader Program object
 */
ShaderProgram::~ShaderProgram() {
    delete this->m_program;
    this->m_program = 0;
}

/**
 * @brief Bind shader program to active OpenGL context
 *
 * @return true on success
 * @return false on failure
 */
bool ShaderProgram::bind() {
    return this->m_program->bind();
}

/**
 * @brief Release shader program from active OpenGL context
 */
void ShaderProgram::release() {
    this->m_program->release();
}

/**
 * @brief Bind attributes to the shader based on its type
 *
 * @param type shader program type
 */
void ShaderProgram::add_attributes(ShaderProgramType type) {
    switch (type) {
        case ShaderProgramType::ModelShader:
        case ShaderProgramType::AxesShader:
        case ShaderProgramType::SilhouetteShader:
            this->m_program->bindAttributeLocation("position", 0);
            this->m_program->bindAttributeLocation("normal", 1);
            break;
        default:
            // no attributes for the other types
            break;
    }
}

/**
 * @brief Bind uniforms to the shader based on its type
 *
 * @param type shader program type
 */
void ShaderProgram::add_uniforms(ShaderProgramType type) {
    switch (type) {
        case ShaderProgramType::ModelShader:
            this->uniforms.emplace("lightpos", this->m_program->uniformLocation("lightpos"));
        case ShaderProgramType::AxesShader:  // intentional fallthrough for ModelShader
            this->uniforms.emplace("mvp", this->m_program->uniformLocation("mvp"));
            this->uniforms.emplace("model", this->m_program->uniformLocation("model"));
            this->uniforms.emplace("view", this->m_program->uniformLocation("view"));
            this->uniforms.emplace("color", this->m_program->uniformLocation("color"));
            break;
        case ShaderProgramType::SilhouetteShader:
        case ShaderProgramType::TextShader:
            this->uniforms.emplace("mvp", this->m_program->uniformLocation("mvp"));
            this->uniforms.emplace("color", this->m_program->uniformLocation("color"));
            break;
        case ShaderProgramType::CanvasShader:
            this->uniforms.emplace("silhouette_texture", this->m_program->uniformLocation("silhouette_texture"));
            this->uniforms.emplace("labels_texture", this->m_program->uniformLocation("labels_texture"));
            this->uniforms.emplace("structure_texture", this->m_program->uniformLocation("structure_texture"));
            break;
        case ShaderProgramType::StereoscopicShader:
            this->uniforms.emplace("left_eye_texture", this->m_program->uniformLocation("left_eye_texture"));
            this->uniforms.emplace("right_eye_texture", this->m_program->uniformLocation("right_eye_texture"));
            this->uniforms.emplace("screen_x", this->m_program->uniformLocation("screen_x"));
            this->uniforms.emplace("screen_y", this->m_program->uniformLocation("screen_y"));
            break;
        default:
            throw std::runtime_error("Unexpected shader program type encountered.");
    }
}
