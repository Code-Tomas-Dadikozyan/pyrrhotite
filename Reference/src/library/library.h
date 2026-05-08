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

#ifndef LIBRARY_LIBRARY_H
#define LIBRARY_LIBRARY_H

#include <algorithm>
#include <memory>
#include <random>
#include <string>
#include <vector>
#include "../practice/practice_config.h"
#include "library_item.h"
#include "library_package.h"

class Library {
private:
    std::vector<LibraryItem> items;
    bool items_sorted = false;

    std::shared_ptr<PracticeConfig> practice_config;
    std::vector<unsigned int> practice_subset;
    unsigned int practice_subset_index;
    bool practice_subset_generated = false;

    std::mt19937 random_engine;

public:
    /**
     * @brief Construct a new Library object
     *
     * @param include_built_in_library whether to immediately load the library
     * built in to this program. Only set this to `false` for testing purposes!
     */
    Library(bool include_built_in_library = true);

    /**
     * @brief Get the items in the library
     *
     * @return std::vector<LibraryItem>&
     */
    std::vector<LibraryItem>& get_items();

    /**
     * @brief Get a random practice item from the library
     *
     * @return LibraryItem&
     */
    LibraryItem& get_practice_item();

    /**
     * @brief Set the practice config object
     *
     * @param practice_config
     */
    void set_practice_config(const std::shared_ptr<PracticeConfig> practice_config);

    /**
     * @brief Add items from a package
     *
     * @param path path to the package metadata file
     */
    void add_items_from_package(const std::string path);

private:
    /**
     * @brief Generate the subset of library items available for practice
     */
    void generate_practice_subset();
};

#endif  // LIBRARY_LIBRARY_H
