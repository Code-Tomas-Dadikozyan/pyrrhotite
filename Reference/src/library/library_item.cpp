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

#include "library_item.h"

/**
 * @brief Construct a new LibraryItem object
 *
 * @param path path of the XYZ file
 * @param name name of the structure
 * @param chemical_formula chemical formula of the structure
 * @param point_group_label point group label of the structure
 * @param item_practice_config practice configuration of the structure
 */
LibraryItem::LibraryItem(const std::string path,
                         const std::string name,
                         const std::string chemical_formula,
                         const PointGroupLabel point_group_label,
                         const json item_practice_config) {
    this->path = path;
    this->name = name;
    this->chemical_formula = chemical_formula;
    this->point_group_label = point_group_label;
    this->item_practice_config = item_practice_config;
}

/**
 * @brief Get the path of the item
 *
 * @return const std::string&
 */
const std::string& LibraryItem::get_path() const {
    return this->path;
}

/**
 * @brief Get the name of the item
 *
 * @return const std::string&
 */
const std::string& LibraryItem::get_name() const {
    return this->name;
}

/**
 * @brief Get the chemical formula of the item
 *
 * @return const std::string&
 */
const std::string& LibraryItem::get_chemical_formula() const {
    return this->chemical_formula;
}

/**
 * @brief Get the point group label of the item
 *
 * @return const PointGroupLabel&
 */
const PointGroupLabel& LibraryItem::get_point_group_label() const {
    return this->point_group_label;
}

/**
 * @brief Get the practice configuration of the item
 *
 * @return const json&
 */
const json& LibraryItem::get_item_practice_config() const {
    return this->item_practice_config;
}

/**
 * @brief Get whether this item can appear in a practice session given the
 * provided practice configuration
 *
 * @param practice_config practice configuration
 * @return true
 * @return false
 */
const bool LibraryItem::can_appear_in_practice(const std::shared_ptr<PracticeConfig> practice_config) {
    json& config = this->item_practice_config;

    for (PracticeModule practice_module : practice_config->get_enabled_modules()) {
        std::string key = PracticeModules::get_key(practice_module);
        if (!(config.contains(key) && config[key].contains("enabled") && config[key]["enabled"])) {
            return false;
        }
    }
    return true;
}

/**
 * @brief Less than operator
 *
 * @param other
 * @return true
 * @return false
 */
bool LibraryItem::operator<(const LibraryItem& other) const {
    return this->name < other.get_name();
}
