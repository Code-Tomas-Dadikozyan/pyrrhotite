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

#include "practice_flowchart_steps.h"

/**
 * @brief Mapping from step key to step object
 */
const std::unordered_map<std::string, PracticeFlowchartStep> PracticeFlowchartSteps::steps = {
    // {key, {text, type, next_keys, check_answer_func}}
    {"start", {
        "Is this molecule linear?",
        Type::NoYes,
        {"higher_order", "linear"},
        [](std::shared_ptr<Symmetry> symmetry) {
            return (int) (symmetry->get_rotor_class() == RotorClass::Linear);
        }
    }},
    {"linear", {
        "Does this molecule contain an inversion center?",
        Type::NoYes,
        {"Cinfv", "Dinfh"},
        [](std::shared_ptr<Symmetry> symmetry) {
            return (int) (symmetry->get_operation_manager()->get_inversions().size() > 0);
        }
    }},
    {"higher_order", {
        "Does this molecule have two or more <i>C<sub>n</sub></i>, with <i>n</i> > 2?",
        Type::NoYes,
        {"C", "high_sym"},
        [](std::shared_ptr<Symmetry> symmetry) {
            std::unordered_map<unsigned int, unsigned int> operation_counter;
            for (Operation& operation : symmetry->get_operation_manager()->get_operations()) {
                if (operation.get_label().get_element() == OperationLabel::Element::ProperRotation &&
                    operation.get_label().get_degree() > 2)
                    ++operation_counter[operation.get_label().get_degree()];
            }
            for (auto& it : operation_counter) {
                if (it.second >= 2) return 1;
            }
            return 0;
        }
    }},
    {"high_sym", {
        "Does this molecule contain an inversion center?",
        Type::NoYes,
        {"Td", "C5"},
        [](std::shared_ptr<Symmetry> symmetry) {
            return (int) (symmetry->get_operation_manager()->get_inversions().size() > 0);
        }
    }},
    {"C5", {
        "Does this molecule contain a <i>C</i><sub>5</sub> axis?",
        Type::NoYes,
        {"Oh", "Ih"},
        [](std::shared_ptr<Symmetry> symmetry) {
            unsigned int count = 0;
            for (Operation& operation : symmetry->get_operation_manager()->get_operations()) {
                if (operation.get_label().get_element() == OperationLabel::Element::ProperRotation &&
                    operation.get_label().get_degree() == 5) count++;
            }
            return (int) (count > 0);
        }
    }},
    {"C", {
        "Does this molecule have at least one proper rotational axis?",
        Type::NoYes,
        {"no_C", "yes_C"},
        [](std::shared_ptr<Symmetry> symmetry) {
            return (int) (symmetry->get_operation_manager()->get_proper_rotations().size() > 0);
        }
    }},
    {"yes_C", {
        "Select the highest-order proper rotational axis (<i>C</i><sub><i>n</i></sub>).",
        Type::ChooseN,
        {"nC2"},
        [](std::shared_ptr<Symmetry> symmetry) {
            unsigned int highest_order = 0;
            for (Operation& operation : symmetry->get_operation_manager()->get_operations()) {
                if (operation.get_label().get_element() == OperationLabel::Element::ProperRotation &&
                    operation.get_label().get_degree() > highest_order)
                    highest_order = operation.get_label().get_degree();
            }
            return highest_order;
        }
    }},
    {"nC2", {
        "Are there {n} <i>C</i><sub>2</sub> axes perpendicular to the highest-order axis?",
        Type::NoYes,
        {"C_horizontal", "D_horizontal"},
        [](std::shared_ptr<Symmetry> symmetry) {
            PointGroupLabel::Class point_group_class = symmetry->get_point_group().get_label().get_class();
            return (int) (point_group_class == PointGroupLabel::Class::D ||
                point_group_class == PointGroupLabel::Class::Dh ||
                point_group_class == PointGroupLabel::Class::Dd);
        }
    }},
    {"D_horizontal", {
        "Does this molecule contain a horizontal reflection plane (<i>σ</i><sub>h</sub>)?",
        Type::NoYes,
        {"D_dihedral", "Dnh"},
        [](std::shared_ptr<Symmetry> symmetry) {
            unsigned int count = 0;
            for (Operation& operation : symmetry->get_operation_manager()->get_operations()) {
                if (operation.get_label().get_element() == OperationLabel::Element::Reflection &&
                    operation.get_label().get_plane() == OperationLabel::Plane::Horizontal) count++;
            }
            return (int) (count > 0);
        }
    }},
    {"D_dihedral", {
        "Does this molecule contain {n} dihedral reflection planes (<i>σ</i><sub>d</sub>)?",
        Type::NoYes,
        {"Dn", "Dnd"},
        [](std::shared_ptr<Symmetry> symmetry) {
            unsigned int count = 0;
            for (Operation& operation : symmetry->get_operation_manager()->get_operations()) {
                if (operation.get_label().get_element() == OperationLabel::Element::Reflection &&
                    operation.get_label().get_plane() == OperationLabel::Plane::Dihedral) count++;
            }
            return (int) (count > 0);  // exact number is not important
        }
    }},
    {"C_horizontal", {
        "Does this molecule contain a horizontal reflection plane (<i>σ</i><sub>h</sub>)?",
        Type::NoYes,
        {"C_vertical", "Cnh"},
        [](std::shared_ptr<Symmetry> symmetry) {
            unsigned int count = 0;
            for (Operation& operation : symmetry->get_operation_manager()->get_operations()) {
                if (operation.get_label().get_element() == OperationLabel::Element::Reflection &&
                    operation.get_label().get_plane() == OperationLabel::Plane::Horizontal) count++;
            }
            return (int) (count > 0);
        }
    }},
    {"C_vertical", {
        "Does this molecule contain {n} vertical reflection planes (<i>σ</i><sub>v</sub>)?",
        Type::NoYes,
        {"imp_rot", "Cnv"},
        [](std::shared_ptr<Symmetry> symmetry) {
            unsigned int count = 0;
            for (Operation& operation : symmetry->get_operation_manager()->get_operations()) {
                if (operation.get_label().get_element() == OperationLabel::Element::Reflection &&
                    operation.get_label().get_plane() == OperationLabel::Plane::Vertical) count++;
            }
            return (int) (count > 0);  // exact number is not important
        }
    }},
    {"imp_rot", {
        "Does this molecule contain an improper rotational axis (<i>S</i><sub>{2n}</sub>)?",
        Type::NoYes,
        {"Cn", "S2n"},
        [](std::shared_ptr<Symmetry> symmetry) {
            return (int) (symmetry->get_operation_manager()->get_improper_rotations().size() > 0);
        }
    }},
    {"no_C", {
        "Does this molecule contain a horizontal reflection plane (<i>σ</i><sub>h</sub>)?",
        Type::NoYes,
        {"nothing", "Cs"},
        [](std::shared_ptr<Symmetry> symmetry) {
            unsigned int count = 0;
            for (Operation& operation : symmetry->get_operation_manager()->get_operations()) {
                if (operation.get_label().get_element() == OperationLabel::Element::Reflection &&
                    operation.get_label().get_plane() == OperationLabel::Plane::Horizontal) count++;
            }
            return (int) (count > 0);
        }
    }},
    {"nothing", {
        "Does this molecule contain an inversion center?",
        Type::NoYes,
        {"C1", "Ci"},
        [](std::shared_ptr<Symmetry> symmetry) {
            return (int) (symmetry->get_operation_manager()->get_inversions().size() == 1);
        }
    }},
    // {key, {text, type, point_group_label}}
    {"Dinfh", {
        "You determined the point group to be <i>D</i><sub>∞h</sub>.",
        Type::Result,
        PointGroupLabel(Class::Dinfh)
    }},
    {"Cinfv", {
        "You determined the point group to be <i>C</i><sub>∞v</sub>.",
        Type::Result,
        PointGroupLabel(Class::Cinfv)
    }},
    {"Ih", {
        "You determined the point group to be <i>I</i><sub>h</sub>.",
        Type::Result,
        PointGroupLabel(Class::Ih)
    }},
    {"Oh", {
        "You determined the point group to be <i>O</i><sub>h</sub>.",
        Type::Result,
        PointGroupLabel(Class::Oh)
    }},
    {"Td", {
        "You determined the point group to be <i>T</i><sub>d</sub>.",
        Type::Result,
        PointGroupLabel(Class::Td)
    }},
    {"Dnh", {
        "You determined the point group to be <i>D</i><sub>{n}h</sub>.",
        Type::Result,
        PointGroupLabel(Class::Dh)  // order depends on previous input
    }},
    {"Dnd", {
        "You determined the point group to be <i>D</i><sub>{n}d</sub>.",
        Type::Result,
        PointGroupLabel(Class::Dd)  // order depends on previous input
    }},
    {"Dn", {
        "You determined the point group to be <i>D</i><sub>{n}</sub>.",
        Type::Result,
        PointGroupLabel(Class::D)  // order depends on previous input
    }},
    {"Cnh", {
        "You determined the point group to be <i>C</i><sub>{n}h</sub>.",
        Type::Result,
        PointGroupLabel(Class::Ch)  // order depends on previous input
    }},
    {"Cnv", {
        "You determined the point group to be <i>C</i><sub>{n}v</sub>.",
        Type::Result,
        PointGroupLabel(Class::Cv)  // order depends on previous input
    }},
    {"S2n", {
        "You determined the point group to be <i>S</i><sub>{2n}</sub>.",
        Type::Result,
        PointGroupLabel(Class::S)  // order depends on previous input
    }},
    {"Cn", {
        "You determined the point group to be <i>C</i><sub>{n}</sub>.",
        Type::Result,
        PointGroupLabel(Class::C)  // order depends on previous input
    }},
    {"Cs", {
        "You determined the point group to be <i>C</i><sub>s</sub>.",
        Type::Result,
        PointGroupLabel(Class::Cs)
    }},
    {"Ci", {
        "You determined the point group to be <i>C</i><sub>i</sub>.",
        Type::Result,
        PointGroupLabel(Class::Ci)
    }},
    {"C1", {
        "You determined the point group to be <i>C</i><sub>1</sub>.",
        Type::Result,
        PointGroupLabel(Class::C, 1)
    }}
};

/**
 * @brief Step key of first step
 */
const std::string PracticeFlowchartSteps::first_step = "start";

/**
 * @brief Get the step object from a key
 *
 * @param key step key
 * @return PracticeFlowchartStep step object
 */
PracticeFlowchartStep PracticeFlowchartSteps::get_step(const std::string key) {
    if (key.empty()) {
        throw std::runtime_error("No key supplied to get_step.");
    }

    std::unordered_map<std::string, PracticeFlowchartStep>::const_iterator it =
        PracticeFlowchartSteps::steps.find(key);

    if (it == PracticeFlowchartSteps::steps.end()) {
        throw std::runtime_error("Invalid key encountered: " + key);
    }

    return it->second;
}
