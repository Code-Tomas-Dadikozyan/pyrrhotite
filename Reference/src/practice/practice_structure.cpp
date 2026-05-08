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

#include "practice_structure.h"

/**
 * @brief Construct a new PracticeStructure object
 *
 * @param symmetry
 * @param use_random whether to use a RNG to generate practice properties.
 * Only set this to `false` for testing purposes!
 */
PracticeStructure::PracticeStructure(std::shared_ptr<Symmetry> symmetry, bool use_random) {
    this->symmetry = symmetry;
    this->use_random = use_random;

    std::random_device device;
    this->random_engine = std::mt19937(device());
}

/**
 * @brief Get the symmetry object
 *
 * @return const std::shared_ptr<Symmetry>
 */
const std::shared_ptr<Symmetry> PracticeStructure::get_symmetry() const {
    return this->symmetry;
}

/**
 * @brief Get the basis set object (generate one if none exists yet)
 *
 * @return const std::shared_ptr<BasisSet>
 */
const std::shared_ptr<BasisSet> PracticeStructure::get_basis_set() {
    if (!this->basis_set_generated) this->generate_basis_set();
    return this->basis_set;
}

/**
 * @brief Get the base atom index (generate one if none exists yet)
 * The base atom index is with respect to the basis set, not the structure!
 *
 * @return const unsigned int
 */
const unsigned int PracticeStructure::get_base_atom() {
    if (!this->base_atom_generated) this->generate_base_atom();
    return this->base_atom;
}

/**
 * @brief Generate a random basis set object
 */
void PracticeStructure::generate_basis_set() {
    std::shared_ptr<Structure> structure = this->symmetry->get_structure();

    json practice_config = structure->get_library_item()->get_item_practice_config();
    if (!practice_config.contains("basis_sets")) {
        throw std::runtime_error("No basis sets defined for the structure");
    }

    json& basis_sets = practice_config["basis_sets"];

    std::uniform_int_distribution<> dist(0, basis_sets.size() - 1);
    int index = (this->use_random) ? dist(this->random_engine) : 0;

    this->basis_set = std::make_shared<BasisSet>(basis_sets[index], this->symmetry);
    this->basis_set_generated = true;
}

/**
 * @brief Generate a random base atom index
 */
void PracticeStructure::generate_base_atom() {
    if (!this->basis_set_generated) {
        throw std::runtime_error("Cannot generate base atom without basis set");
    }

    const std::vector<unsigned int>& basis_set_atoms = this->basis_set->get_atoms();

    std::uniform_int_distribution<> dist(0, basis_set_atoms.size() - 1);
    int index = (this->use_random) ? dist(this->random_engine) : 0;

    this->base_atom = index;  // with respect to basis set
    this->base_atom_generated = true;
}
