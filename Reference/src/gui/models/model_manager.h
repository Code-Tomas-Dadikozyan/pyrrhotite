/**
 * Schoenflies
 * Copyright (c) 2022 Luuk Kempen
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

#ifndef GUI_MODELS_MODEL_MANAGER_H
#define GUI_MODELS_MODEL_MANAGER_H

#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_map>
#include "model.h"

class ModelManager {
private:
    std::unordered_map<std::string, std::unique_ptr<Model>> model_map;

public:
    /**
     * @brief Construct a new Model Manager object
     */
    ModelManager();

    /**
     * @brief Get pointer to a model
     *
     * @param name name of the model
     * @return Model* pointer to model
     */
    Model* get_model(const std::string& name);

    /**
     * @brief Add a new model
     *
     * @param name model name
     * @param model model object
     */
    void add_model(const std::string& name, std::unique_ptr<Model> model);

    /**
     * @brief Load all models to their vertex array objects
     */
    void load_models_to_vao();
};

#endif  // GUI_MODELS_MODEL_MANAGER_H
