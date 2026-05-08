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

#ifndef GUI_MODELS_MODEL_INSTANCE_H
#define GUI_MODELS_MODEL_INSTANCE_H

#include <glm/glm.hpp>
#include <string>

struct ModelInstance {
    std::string model_name;
    glm::mat4x4 transform;
    glm::vec4 colour;
    int texture_id;
};

#endif  // GUI_MODELS_MODEL_INSTANCE_H
