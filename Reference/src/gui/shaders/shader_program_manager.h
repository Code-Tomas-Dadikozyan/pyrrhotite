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

#ifndef GUI_SHADERS_SHADER_PROGRAM_MANAGER_H
#define GUI_SHADERS_SHADER_PROGRAM_MANAGER_H

#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include <QString>
#include "shader_program.h"
#include "shader_program_type.h"

class ShaderProgramManager {
private:
    std::unordered_map<std::string, std::unique_ptr<ShaderProgram>> shader_program_map;

public:
    /**
     * @brief Construct a new Shader Program Manager object
     */
    ShaderProgramManager();

    /**
     * @brief Get pointer to a shader program
     *
     * @param name name of the shader program
     * @return ShaderProgram* pointer to shader program
     */
    ShaderProgram* get_shader_program(const std::string& name);

    /**
     * @brief Create and return a new shader program object
     *
     * @param name shader program name
     * @param type shader program type
     * @param vertex_filename filename of vertex shader
     * @param fragment_filename filename of fragment shader
     * @return ShaderProgram* pointer to new shader program
     */
    ShaderProgram* create_shader_program(const std::string& name, const ShaderProgramType type, const QString& vertex_filename, const QString& fragment_filename);

    /**
     * @brief Bind shader program to active OpenGL context by name
     *
     * @param name name of shader program
     * @return true on success
     * @return false on failure
     */
    bool bind(const std::string& name);

    /**
     * @brief Release shader program from active OpenGL context by name
     *
     * @param name name of shader program
     */
    void release(const std::string& name);
};

#endif  // GUI_SHADERS_SHADER_PROGRAM_MANAGER_H
