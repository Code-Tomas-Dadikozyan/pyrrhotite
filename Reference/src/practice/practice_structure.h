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

#ifndef PRACTICE_PRACTICE_STRUCTURE_H
#define PRACTICE_PRACTICE_STRUCTURE_H

#include <algorithm>
#include <memory>
#include <random>
#include <stdexcept>
#include <nlohmann/json.hpp>
#include "../symmetry/symmetry.h"
#include "../basis_set.h"
#include "../structure.h"

using json = nlohmann::json;

class PracticeStructure {
private:
    std::shared_ptr<Symmetry> symmetry;
    bool use_random;

    bool basis_set_generated = false;
    std::shared_ptr<BasisSet> basis_set;

    bool base_atom_generated = false;
    unsigned int base_atom;

    std::mt19937 random_engine;

public:
    /**
     * @brief Construct a new PracticeStructure object
     *
     * @param symmetry
     * @param use_random whether to use a RNG to generate practice properties.
     * Only set this to `false` for testing purposes!
     */
    PracticeStructure(std::shared_ptr<Symmetry> symmetry, bool use_random = true);

    /**
     * @brief Get the symmetry object
     *
     * @return const std::shared_ptr<Symmetry>
     */
    const std::shared_ptr<Symmetry> get_symmetry() const;

    /**
     * @brief Get the basis set object (generate one if none exists yet)
     *
     * @return const std::shared_ptr<BasisSet>
     */
    const std::shared_ptr<BasisSet> get_basis_set();

    /**
     * @brief Get the base atom index (generate one if none exists yet)
     * The base atom index is with respect to the basis set, not the structure!
     *
     * @return const unsigned int
     */
    const unsigned int get_base_atom();

private:
    /**
     * @brief Generate a random basis set object
     */
    void generate_basis_set();

    /**
     * @brief Generate a random base atom index
     */
    void generate_base_atom();
};

#endif  // PRACTICE_PRACTICE_STRUCTURE_H
