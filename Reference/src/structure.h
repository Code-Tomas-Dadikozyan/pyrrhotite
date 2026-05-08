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

#ifndef STRUCTURE_H
#define STRUCTURE_H

#define GLM_ENABLE_EXPERIMENTAL

#include <math.h>
#include <memory>
#include <stdexcept>
#include <string>
#include <unordered_set>
#include <utility>
#include <vector>
#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>
#include <boost/lexical_cast.hpp>
#include <glm/glm.hpp>
#include <glm/gtx/norm.hpp>
#include "library/library_item.h"
#include "periodic_table/periodic_table.h"
#include "symmetry/operations/operation.h"
#include "file.h"

class Operation;  // forward declaration

class Structure {
private:
    unsigned int num_atoms;
    std::vector<glm::vec3> coordinates;
    std::vector<unsigned int> atomic_numbers;
    std::string description;
    std::string filename;

    std::shared_ptr<LibraryItem> library_item;

public:
    /**
     * @brief Default constructor
     */
    Structure();

    /**
     * @brief Construct a new Structure object from a file
     *
     * @param path
     */
    Structure(const std::string& path);

    /**
     * @brief Get the number of atoms in the structure
     *
     * @return const unsigned int
     */
    const unsigned int get_num_atoms() const;

    /**
     * @brief Get the coordinates of the atoms in the structure
     *
     * @return const std::vector<glm::vec3>&
     */
    const std::vector<glm::vec3>& get_coordinates() const;

    /**
     * @brief Get the coordinates of an atom in the structure by index
     *
     * @param index index of atom
     * @return const glm::vec3
     */
    const glm::vec3 get_coordinates(unsigned int index) const;

    /**
     * @brief Get the atomic numbers of the atoms in the structure
     *
     * @return const std::vector<unsigned int>&
     */
    const std::vector<unsigned int>& get_atomic_numbers() const;

    /**
     * @brief Get the atomic number of an atom in the structure by index
     *
     * @param index index of atom
     * @return const unsigned int
     */
    const unsigned int get_atomic_number(unsigned int index) const;

    /**
     * @brief Get the description of the structure
     *
     * @return const std::string&
     */
    const std::string& get_description() const;

    /**
     * @brief Get the filename of the structure
     *
     * @return const std::string&
     */
    const std::string& get_filename() const;

    /**
     * @brief Get a combination of description and filename of the structure
     *
     * @return const std::string
     */
    const std::string get_description_filename() const;

    /**
     * @brief Calculate pairs of elements between which bonds are (likely) formed
     *
     * @return const std::vector<std::pair<unsigned int, unsigned int>>
     */
    const std::vector<std::pair<unsigned int, unsigned int>> calculate_bond_pairs() const;

    /**
     * @brief Get the list of highlighted atoms
     *
     * @return const std::unordered_set<unsigned int>&
     */
    const std::unordered_set<unsigned int>& get_highlighted_atoms() const;

    /**
     * @brief Get the library item object
     *
     * @return const std::shared_ptr<LibraryItem>
     */
    const std::shared_ptr<LibraryItem> get_library_item() const;

    /**
     * @brief Set the library item object
     *
     * @param library_item
     */
    void set_library_item(const std::shared_ptr<LibraryItem> library_item);

    /**
     * @brief Find the index of the closest atom of the element given by the
     * provided atomic number to the provided coordinates
     *
     * @param coordinates coordinates around which the closest atom should be
     * found
     * @param atomic_number atomic number of the atom that should be found
     * @return const unsigned int index of the closest atom with the given
     * atomic number
     */
    const unsigned int find_closest_index(glm::vec3 coordinates, unsigned int atomic_number) const;

private:
    /**
     * @brief Load structure from file
     *
     * @param path
     */
    void load_from_file(const std::string& path);

    /**
     * @brief Load structure from xyz file
     *
     * @param path
     */
    void load_from_xyz(const std::string& path);

    /**
     * @brief Centre the structure at its centre of mass
     */
    void centre_at_com();
};

#endif  // STRUCTURE_H
