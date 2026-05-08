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

#include "practice_flowchart.h"

/**
 * @brief Default constructor
 */
PracticeFlowchart::PracticeFlowchart() {}

/**
 * @brief Construct a new Practice Flowchart object
 *
 * @param practice_structure practice structure object
 */
PracticeFlowchart::PracticeFlowchart(std::shared_ptr<PracticeStructure> practice_structure) {
    this->practice_structure = practice_structure;
    this->add_step(PracticeFlowchartSteps::first_step);
}

/**
 * @brief Handle an answer given to a step
 *
 * @param step_index step index
 * @param answer given answer
 * @return bool if anything was changed
 */
bool PracticeFlowchart::handle_answer(int step_index, int answer) {
    // clear steps after this step
    for (int i = this->steps_taken.size() - 1; i > step_index; --i) {
        this->steps_taken.erase(this->steps_taken.begin() + i);
    }

    auto step = this->steps_taken[step_index];

    if (step->get_type() != PracticeFlowchartStep::Type::Result) {
        if (step->get_type() == PracticeFlowchartStep::Type::ChooseN) {
            this->n = answer;
        }

        // add next step
        switch (step->get_type()) {
            case PracticeFlowchartStep::Type::NoYes:
                this->add_step(step->get_next_keys()[answer]);
                return true;
            case PracticeFlowchartStep::Type::ChooseN:
                this->add_step(step->get_next_keys()[0]);
                return true;
        }
    }

    return false;
}

/**
 * @brief Get a step by index
 *
 * @param step_index step index
 * @return std::shared_ptr<PracticeFlowchartStep>
 */
std::shared_ptr<PracticeFlowchartStep> PracticeFlowchart::get_step(int step_index) {
    if (step_index >= this->steps_taken.size()) {
        throw std::runtime_error("Invalid step index encountered: " + step_index);
    }
    return this->steps_taken[step_index];
}

/**
 * @brief Get the index of the latest step
 *
 * @return unsigned int
 */
unsigned int PracticeFlowchart::get_latest_step_index() {
    return this->steps_taken.size() - 1;
}

/**
 * @brief Add a step to the flowchart by key
 *
 * @param key
 */
void PracticeFlowchart::add_step(std::string key) {
    auto step = std::make_shared<PracticeFlowchartStep>(PracticeFlowchartSteps::get_step(key));
    step->calculate_correct_answer(this->practice_structure->get_symmetry());
    step->set_n(this->n);
    this->steps_taken.push_back(step);
}
