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

#include "shader_program_manager.h"

/**
 * @brief Construct a new Shader Program Manager object
 */
ShaderProgramManager::ShaderProgramManager() {}

/**
 * @brief Get pointer to a shader program
 *
 * @param name name of the shader program
 * @return ShaderProgram* pointer to shader program
 */
ShaderProgram* ShaderProgramManager::get_shader_program(const std::string& name) {
    auto it = this->shader_program_map.find(name);

    if (it == this->shader_program_map.end()) {
        throw std::logic_error("Invalid shader program encountered: " + name);
    }

    return it->second.get();
}

/**
 * @brief Create and return a new shader program object
 *
 * @param name shader program name
 * @param type shader program type
 * @param vertex_filename filename of vertex shader
 * @param fragment_filename filename of fragment shader
 * @return ShaderProgram* pointer to new shader program
 */
ShaderProgram* ShaderProgramManager::create_shader_program(const std::string& name, const ShaderProgramType type, const QString& vertex_filename, const QString& fragment_filename) {
    ShaderProgram* m_program = new ShaderProgram(name, type, vertex_filename, fragment_filename);

    this->shader_program_map.emplace(name, m_program);

    return m_program;
}

/**
 * @brief Bind shader program to active OpenGL context by name
 *
 * @param name name of shader program
 * @return true on success
 * @return false on failure
 */
bool ShaderProgramManager::bind(const std::string& name) {
    return this->get_shader_program(name)->bind();
}

/**
 * @brief Release shader program from active OpenGL context by name
 *
 * @param name name of shader program
 */
void ShaderProgramManager::release(const std::string& name) {
    this->get_shader_program(name)->release();
}
