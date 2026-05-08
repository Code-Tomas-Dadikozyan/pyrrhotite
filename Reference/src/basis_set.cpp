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

#include "basis_set.h"

/**
 * @brief Construct a new BasisSet object
 *
 * @param basis_set JSON basis set configuration
 * @param symmetry symmetry
 */
BasisSet::BasisSet(json& basis_set, std::shared_ptr<Symmetry> symmetry) {
    if (!basis_set.contains("element")) {
        throw std::runtime_error("Invalid basis set: element is missing");
    }
    if (!basis_set.contains("orbital")) {
        throw std::runtime_error("Invalid basis set: orbital is missing");
    }

    std::string element = basis_set["element"];
    std::string orbital = basis_set["orbital"];

    unsigned int atomic_number = PeriodicTable::get_atomic_number(element);
    this->element = PeriodicTable::get_element(atomic_number);
    this->orbital_label = OrbitalLabel::get_orbital_label(orbital);

    if (this->orbital_label.get_azimuthal() == 1) {  // p
        switch (this->orbital_label.get_magnetic()) {
            case -1:  // y
                this->orbital_vector = symmetry->get_y_axis();
                break;
            case 0:  // z
                this->orbital_vector = symmetry->get_z_axis();
                break;
            case 1:  // x
                this->orbital_vector = symmetry->get_x_axis();
                break;
        }
    }

    for (unsigned int i = 0; i < symmetry->get_structure()->get_num_atoms(); ++i) {
        if (symmetry->get_structure()->get_atomic_number(i) == atomic_number) this->atoms.push_back(i);
    }
}

/**
 * @brief Get the element
 *
 * @return const Element&
 */
const Element& BasisSet::get_element() const {
    return this->element;
}

/**
 * @brief Get the orbital label
 *
 * @return const OrbitalLabel&
 */
const OrbitalLabel& BasisSet::get_orbital_label() const {
    return this->orbital_label;
}

/**
 * @brief Get the orbital vector
 *
 * @return const glm::vec3&
 */
const glm::vec3& BasisSet::get_orbital_vector() const {
    return this->orbital_vector;
}

/**
 * @brief Get the atoms in the basis set
 *
 * @return const std::vector<unsigned int>&
 */
const std::vector<unsigned int>& BasisSet::get_atoms() const {
    return this->atoms;
}
