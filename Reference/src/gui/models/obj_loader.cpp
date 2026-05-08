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

#include "obj_loader.h"

/**
 * @brief Create a unique pointer to a model from an obj file
 *
 * @param path path to the obj file (can be Qt resource path)
 * @return std::unique_ptr<Model3D>
 */
std::unique_ptr<Model3D> ObjLoader::load_from_obj(const std::string& path) {
    // we use QFile here instead of std::ifstream (such as in src/structure.cpp)
    // so that resource paths can be loaded
    QFile file(QString::fromStdString(path));

    if (!file.open(QIODevice::OpenModeFlag::ReadOnly | QIODevice::OpenModeFlag::Text)) {
        throw std::runtime_error("Could not open file: " + path);
    }

    QTextStream ifs(&file);

    QString line;  // container for ifs.readLine result
    QRegularExpressionMatch match;  // container for regex matches

    // define regex patterns
    static const QRegularExpression v_line("v\\s+([0-9.-]+)\\s+([0-9.-]+)\\s+([0-9.-]+).*");
    static const QRegularExpression vn_line("vn\\s+([0-9.-]+)\\s+([0-9.-]+)\\s+([0-9.-]+).*");
    static const QRegularExpression f_line("f\\s+([0-9]+)\\/([0-9]+)\\/([0-9]+)\\s+([0-9]+)\\/([0-9]+)\\/([0-9]+)\\s+([0-9]+)\\/([0-9]+)\\/([0-9]+).*");
    static const QRegularExpression f2_line("f\\s+([0-9]+)\\/\\/([0-9]+)\\s+([0-9]+)\\/\\/([0-9]+)\\s+([0-9]+)\\/\\/([0-9]+).*");

    // data holders
    std::vector<glm::vec3> _positions;
    std::vector<glm::vec3> _normals;
    std::vector<unsigned int> position_indices;
    std::vector<unsigned int> normal_indices;

    while (!ifs.atEnd()) {
        QString line = ifs.readLine();

        // positions
        match = v_line.match(line);
        if (match.hasMatch()) {
            _positions.emplace_back(match.captured(1).toFloat(), match.captured(2).toFloat(), match.captured(3).toFloat());
            continue;
        }

        // normals
        match = vn_line.match(line);
        if (match.hasMatch()) {
            _normals.emplace_back(match.captured(1).toFloat(), match.captured(2).toFloat(), match.captured(3).toFloat());
            continue;
        }

        // faces
        match = f_line.match(line);
        if (match.hasMatch()) {
            position_indices.insert(position_indices.end(),
                {match.captured(1).toUInt() - 1, match.captured(4).toUInt() - 1, match.captured(7).toUInt() - 1});
            normal_indices.insert(normal_indices.end(),
                {match.captured(3).toUInt() - 1, match.captured(6).toUInt() - 1, match.captured(9).toUInt() - 1});
            continue;
        }

        match = f2_line.match(line);
        if (match.hasMatch()) {
            position_indices.insert(position_indices.end(),
                {match.captured(1).toUInt() - 1, match.captured(3).toUInt() - 1, match.captured(5).toUInt() - 1});
            normal_indices.insert(normal_indices.end(),
                {match.captured(2).toUInt() - 1, match.captured(4).toUInt() - 1, match.captured(6).toUInt() - 1});
            continue;
        }
    }

    // restructure data
    std::vector<glm::vec3> positions;
    std::vector<glm::vec3> normals;
    std::vector<unsigned int> indices;

    for (unsigned int i = 0; i < position_indices.size(); ++i) {
        positions.push_back(_positions[position_indices[i]]);
        normals.push_back(_normals[normal_indices[i]]);
        indices.push_back(i);
    }

    return std::make_unique<Model3D>(positions, normals, indices);
}
