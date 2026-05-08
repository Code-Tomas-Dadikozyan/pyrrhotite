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

#ifndef GUI_MODELS_OBJ_LOADER_H
#define GUI_MODELS_OBJ_LOADER_H

#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include <glm/glm.hpp>
#include <QFile>
#include <QIODevice>
#include <QRegularExpression>
#include <QRegularExpressionMatch>
#include <QString>
#include <QTextStream>
#include "model_3d.h"

class ObjLoader final {
public:
    /**
     * @brief Create a unique pointer to a model from an obj file
     *
     * @param path path to the obj file (can be Qt resource path)
     * @return std::unique_ptr<Model3D>
     */
    static std::unique_ptr<Model3D> load_from_obj(const std::string& path);
};

#endif  // GUI_MODELS_OBJ_LOADER_H
