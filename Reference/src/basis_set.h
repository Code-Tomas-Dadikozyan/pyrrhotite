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

#ifndef BASIS_SET_H
#define BASIS_SET_H

#include <memory>
#include <stdexcept>
#include <string>
#include <vector>
#include <glm/glm.hpp>
#include <nlohmann/json.hpp>
#include "orbitals/orbital_label.h"
#include "periodic_table/element.h"
#include "periodic_table/periodic_table.h"
#include "symmetry/symmetry.h"
#include "structure.h"

using json = nlohmann::json;

class BasisSet {
private:
    Element element;
    OrbitalLabel orbital_label;
    glm::vec3 orbital_vector;

    std::vector<unsigned int> atoms;

public:
    /**
     * @brief Construct a new BasisSet object
     *
     * @param basis_set JSON basis set configuration
     * @param symmetry symmetry
     */
    BasisSet(json& basis_set, std::shared_ptr<Symmetry> symmetry);

    /**
     * @brief Get the element
     *
     * @return const Element&
     */
    const Element& get_element() const;

    /**
     * @brief Get the orbital label
     *
     * @return const OrbitalLabel&
     */
    const OrbitalLabel& get_orbital_label() const;

    /**
     * @brief Get the orbital vector
     *
     * @return const glm::vec3&
     */
    const glm::vec3& get_orbital_vector() const;

    /**
     * @brief Get the atoms in the basis set
     *
     * @return const std::vector<unsigned int>&
     */
    const std::vector<unsigned int>& get_atoms() const;
};

#endif  // BASIS_SET_H
