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

#ifndef GUI_SHADERS_SHADER_PROGRAM_H
#define GUI_SHADERS_SHADER_PROGRAM_H

#include <stdexcept>
#include <string>
#include <unordered_map>
#include <QOpenGLShader>
#include <QOpenGLShaderProgram>
#include <QString>
#include "shader_program_type.h"

class ShaderProgram {
private:
    QOpenGLShaderProgram *m_program;

    std::unordered_map<std::string, int> uniforms;

public:
    /**
     * @brief Construct a new Shader Program object
     *
     * @param name shader program name
     * @param type shader program type
     * @param vertex_filename filename of vertex shader
     * @param fragment_filename filename of fragment shader
     */
    ShaderProgram(const std::string& name, const ShaderProgramType type, const QString& vertex_filename, const QString& fragment_filename);

    /**
     * @brief Destroy the Shader Program object
     */
    ~ShaderProgram();

    /**
     * @brief Set a uniform to a value
     *
     * @tparam T type of value
     * @param name
     * @param value
     */
    template <typename T>
    void set_uniform(const std::string& name, T const &value) {
        auto it = this->uniforms.find(name);

        if (it == this->uniforms.end()) {
            throw std::logic_error("Invalid uniform name: " + name);
        }

        this->m_program->setUniformValue(it->second, value);
    }

    /**
     * @brief Bind shader program to active OpenGL context
     *
     * @return true on success
     * @return false on failure
     */
    bool bind();

    /**
     * @brief Release shader program from active OpenGL context
     */
    void release();

private:
    /**
     * @brief Bind attributes to the shader based on its type
     *
     * @param type shader program type
     */
    void add_attributes(ShaderProgramType type);

    /**
     * @brief Bind uniforms to the shader based on its type
     *
     * @param type shader program type
     */
    void add_uniforms(ShaderProgramType type);
};

#endif  // GUI_SHADERS_SHADER_PROGRAM_H
