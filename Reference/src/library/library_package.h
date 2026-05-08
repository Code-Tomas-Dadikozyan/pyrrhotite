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

#ifndef LIBRARY_LIBRARY_PACKAGE_H
#define LIBRARY_LIBRARY_PACKAGE_H

#include <stdexcept>
#include <string>
#include <vector>
#include <boost/filesystem.hpp>
#include <nlohmann/json.hpp>
#include "library_item.h"
#include "../symmetry/point_groups/point_group_label.h"
#include "../file.h"

using json = nlohmann::json;

class LibraryPackage {
private:
    std::string path;
    json metadata;
    boost::filesystem::path root;

public:
    /**
     * @brief Construct a new LibraryPackage object
     *
     * @param path path of package metadata file
     */
    LibraryPackage(const std::string path);

    /**
     * @brief Get an item from the package by index
     *
     * @param index
     * @return LibraryItem
     */
    LibraryItem get_item(unsigned int index);

    /**
     * @brief Get the size of the package
     *
     * @return unsigned int
     */
    unsigned int get_size();
};

#endif  // LIBRARY_LIBRARY_PACKAGE_H
