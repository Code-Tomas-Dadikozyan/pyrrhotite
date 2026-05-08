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

#include "structure.h"

/**
 * @brief Default constructor
 */
Structure::Structure() {}

/**
 * @brief Construct a new Structure object from a file
 *
 * @param path
 */
Structure::Structure(const std::string& path) {
    this->load_from_file(path);

    this->centre_at_com();
}

/**
 * @brief Load structure from file
 *
 * @param path
 */
void Structure::load_from_file(const std::string& path) {
    boost::filesystem::path p(path);
    this->filename = p.filename().string();

    // determine file type
    if (this->filename.find(".xyz") != std::string::npos) {
        this->load_from_xyz(path);
    } else {
        throw std::runtime_error("File is not supported: " + path);
    }
}

/**
 * @brief Load structure from xyz file
 *
 * @param path
 */
void Structure::load_from_xyz(const std::string& path) {
    File file(path);

    std::string line;  // container for std::getline result
    std::vector<std::string> pieces;  // container for boost::split result

    // read number of atoms
    std::getline(file.get_stream(), line);
    boost::trim(line);
    this->num_atoms = boost::lexical_cast<unsigned int>(line);

    // read description
    std::getline(file.get_stream(), line);
    boost::trim(line);
    this->description = line;

    // read atoms
    for (unsigned int i = 0; i < this->num_atoms; ++i) {
        std::getline(file.get_stream(), line);
        boost::trim(line);
        boost::split(pieces, line, boost::is_any_of("\t "), boost::token_compress_on);

        if (pieces.size() == 4) {
            this->atomic_numbers.push_back(PeriodicTable::get_atomic_number(pieces[0]));
            this->coordinates.emplace_back(
                boost::lexical_cast<float>(pieces[1]),
                boost::lexical_cast<float>(pieces[2]),
                boost::lexical_cast<float>(pieces[3])
            );
        } else {
            throw std::runtime_error("File has invalid format: " + path);
        }
    }
}

/**
 * @brief Centre the structure at its centre of mass
 */
void Structure::centre_at_com() {
    glm::vec3 centre_of_mass(0);
    float total_mass = 0;

    for (unsigned int i = 0; i < this->get_num_atoms(); ++i) {
        float mass = PeriodicTable::get_element(this->get_atomic_number(i)).mass;
        centre_of_mass += mass * this->get_coordinates(i);
        total_mass += mass;
    }

    centre_of_mass /= total_mass;

    for (unsigned int i = 0; i < this->get_num_atoms(); ++i) {
        this->coordinates[i] -= centre_of_mass;
    }
}

/**
 * @brief Get the number of atoms in the structure
 *
 * @return const unsigned int
 */
const unsigned int Structure::get_num_atoms() const {
    return this->num_atoms;
}

/**
 * @brief Get the coordinates of the atoms in the structure
 *
 * @return const std::vector<glm::vec3>&
 */
const std::vector<glm::vec3>& Structure::get_coordinates() const {
    return this->coordinates;
}

/**
 * @brief Get the coordinates of an atom in the structure by index
 *
 * @param index index of atom
 * @return const glm::vec3
 */
const glm::vec3 Structure::get_coordinates(unsigned int index) const {
    if (index < this->get_num_atoms()) {
        return this->coordinates[index];
    } else {
        throw std::runtime_error("Requested invalid atom index.");
    }
}

/**
 * @brief Get the atomic numbers of the atoms in the structure
 *
 * @return const std::vector<unsigned int>&
 */
const std::vector<unsigned int>& Structure::get_atomic_numbers() const {
    return this->atomic_numbers;
}

/**
 * @brief Get the atomic number of an atom in the structure by index
 *
 * @param index index of atom
 * @return const unsigned int
 */
const unsigned int Structure::get_atomic_number(unsigned int index) const {
    if (index < this->get_num_atoms()) {
        return this->atomic_numbers[index];
    } else {
        throw std::runtime_error("Requested invalid atom index.");
    }
}

/**
 * @brief Get the description of the structure
 *
 * @return const std::string&
 */
const std::string& Structure::get_description() const {
    return this->description;
}

/**
 * @brief Get the filename of the structure
 *
 * @return const std::string&
 */
const std::string& Structure::get_filename() const {
    return this->filename;
}

/**
 * @brief Get a combination of description and filename of the structure
 *
 * @return const std::string&
 */
const std::string Structure::get_description_filename() const {
    if (!this->description.empty()) {
        return this->description + " \u2013 " + this->filename;
    } else {
        // only return filename if the description is empty
        return this->filename;
    }
}

/**
 * @brief Calculate pairs of elements between which bonds are (likely) formed
 *
 * @return const std::vector<std::pair<unsigned int, unsigned int>>
 */
const std::vector<std::pair<unsigned int, unsigned int>> Structure::calculate_bond_pairs() const {
    std::vector<std::pair<unsigned int, unsigned int>> pairs;

    for (unsigned int i = 0; i < this->get_num_atoms() - 1; ++i) {
        for (unsigned int j = i + 1; j < this->get_num_atoms(); ++j) {
            float dist2 = glm::length2(this->get_coordinates(i) - this->get_coordinates(j));
            float thres = 20 * PeriodicTable::get_element(this->get_atomic_number(i)).radius *
                PeriodicTable::get_element(this->get_atomic_number(j)).radius;
            if (dist2 < thres) pairs.emplace_back(i, j);
        }
    }

    return pairs;
}

/**
 * @brief Get the library item object
 *
 * @return const std::shared_ptr<LibraryItem>
 */
const std::shared_ptr<LibraryItem> Structure::get_library_item() const {
    return this->library_item;
}

/**
 * @brief Set the library item object
 *
 * @param library_item
 */
void Structure::set_library_item(const std::shared_ptr<LibraryItem> library_item) {
    this->library_item = library_item;
}

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
const unsigned int Structure::find_closest_index(glm::vec3 coordinates, unsigned int atomic_number) const {
    float min_distance2 = INFINITY;
    unsigned int closest_index = -1;

    for (unsigned int i = 0; i < this->get_num_atoms(); ++i) {
        if (this->get_atomic_number(i) != atomic_number) continue;

        float distance2 = glm::distance2(this->get_coordinates(i), coordinates);

        if (distance2 < min_distance2) {
            min_distance2 = distance2;
            closest_index = i;
        }
    }

    return closest_index;
}
