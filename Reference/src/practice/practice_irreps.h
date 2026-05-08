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

#ifndef PRACTICE_PRACTICE_IRREPS_H
#define PRACTICE_PRACTICE_IRREPS_H

#include <memory>
#include <stdexcept>
#include <utility>
#include <vector>
#include <glm/glm.hpp>
#include "../symmetry/irreps/irrep_label.h"
#include "../symmetry/operations/operation.h"
#include "../symmetry/operations/operation_label_count.h"
#include "../symmetry/symmetry.h"
#include "../basis_set.h"
#include "../structure.h"
#include "practice_structure.h"

class PracticeIrreps {
private:
    std::shared_ptr<PracticeStructure> practice_structure;

    std::vector<std::pair<OperationLabelCount, double>> correct_characters;
    std::vector<std::pair<IrrepLabel, double>> correct_irreps;

public:
    /**
     * @brief Default constructor
     */
    PracticeIrreps();

    /**
     * @brief Construct a new Practice Irreps object
     *
     * @param practice_structure practice structure object
     */
    PracticeIrreps(std::shared_ptr<PracticeStructure> practice_structure);

    /**
     * @brief Get the correct character values
     *
     * @return std::vector<std::pair<OperationLabelCount, double>>&
     */
    std::vector<std::pair<OperationLabelCount, double>>& get_correct_characters();

    /**
     * @brief Get the correct irrep values
     *
     * @return std::vector<std::pair<IrrepLabel, double>>
     */
    std::vector<std::pair<IrrepLabel, double>> get_correct_irreps();

private:
    /**
     * @brief Calculate the correct answers to the questions
     */
    void calculate();

    /**
     * @brief Calculate the character of each operation (how many orbitals
     * remain in place)
     */
    void calculate_characters();

    /**
     * @brief Calculate the irreducible representations of the structure
     */
    void calculate_irreps();
};

#endif  // PRACTICE_PRACTICE_IRREPS_H
