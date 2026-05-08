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

#include "library_package.h"

/**
 * @brief Construct a new LibraryPackage object
 *
 * @param path path of package metadata file
 */
LibraryPackage::LibraryPackage(const std::string path) {
    this->path = path;
    this->metadata = json::parse(File(path).get_stream());

    boost::filesystem::path p(path);
    this->root = p.parent_path();
}

/**
 * @brief Get an item from the package by index
 *
 * @param index
 * @return LibraryItem
 */
LibraryItem LibraryPackage::get_item(unsigned int index) {
    if (index >= this->metadata.size()) {
        throw std::runtime_error("Invalid item index encountered: " + index);
    }

    json item = this->metadata[index];

    for (std::string field : {"path", "name", "chemical_formula", "point_group", "practice_config"}) {
        if (!item.contains(field)) throw std::runtime_error("Key " + field + " not found in JSON object");
    }

    std::string path = (this->root / boost::filesystem::path(item["path"])).string();
    std::string name = item["name"];
    std::string chemical_formula = item["chemical_formula"];

    PointGroupLabel::Class point_group_class = PointGroupLabel::get_class(item["point_group"][0]);
    PointGroupLabel point_group_label;
    if (item["point_group"].size() == 1) {
        point_group_label = PointGroupLabel(point_group_class);
    } else if (item["point_group"].size() == 2) {
        point_group_label = PointGroupLabel(point_group_class, item["point_group"][1]);
    } else {
        throw std::runtime_error("Invalid value for key point_group in JSON object");
    }

    json item_practice_config = item["practice_config"];

    return {path, name, chemical_formula, point_group_label, item_practice_config};
}

/**
 * @brief Get the size of the package
 *
 * @return unsigned int
 */
unsigned int LibraryPackage::get_size() {
    return this->metadata.size();
}
