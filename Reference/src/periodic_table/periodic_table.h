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

#ifndef PERIODIC_TABLE_PERIODIC_TABLE_H
#define PERIODIC_TABLE_PERIODIC_TABLE_H

#include <stdexcept>
#include <string>
#include <unordered_map>
#include "element.h"

class PeriodicTable final {
private:
    /**
     * @brief Mapping from element symbol to atomic number
     */
    static const std::unordered_map<std::string, unsigned int> symbol_to_atomic_number;

    /**
     * @brief Mapping from atomic number to Element struct
     */
    static const std::unordered_map<unsigned int, Element> atomic_number_to_element;

public:
    /**
     * @brief Get the atomic number from an element symbol
     *
     * @param element element symbol
     * @return unsigned int atomic number
     */
    static unsigned int get_atomic_number(const std::string& element);

    /**
     * @brief Get the element struct from an atomic number
     *
     * @param atomic_number atomic number
     * @return Element element struct
     */
    static Element get_element(const unsigned int atomic_number);

private:
    /**
     * @brief Default constructor
     */
    PeriodicTable() {}
};

#endif  // PERIODIC_TABLE_PERIODIC_TABLE_H
