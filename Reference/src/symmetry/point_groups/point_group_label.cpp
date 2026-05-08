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

#include "point_group_label.h"

/**
 * @brief Default constructor
 */
PointGroupLabel::PointGroupLabel() {}

/**
 * @brief Construct a new Point Group Label object
 *
 * @param point_group_class class of the point group
 * @param order order of the point group
 */
PointGroupLabel::PointGroupLabel(Class point_group_class, unsigned int order) {
    this->point_group_class = point_group_class;
    this->order = order;
}

/**
 * @brief Construct a new Point Group Label object
 *
 * @param point_group_class class of the point group
 */
PointGroupLabel::PointGroupLabel(Class point_group_class) {
    this->point_group_class = point_group_class;
    this->order = 0;
}

/**
 * @brief Get the class of the point group
 *
 * @return const Class
 */
const PointGroupLabel::Class PointGroupLabel::get_class() const {
    return this->point_group_class;
}

/**
 * @brief Get the order of the point group
 *
 * @return const unsigned int
 */
const unsigned int PointGroupLabel::get_order() const {
    return this->order;
}

/**
 * @brief Get the name of the point group in plaintext
 *
 * @return const std::string
 */
const std::string PointGroupLabel::get_name() const {
    std::string order = std::to_string(this->order);

    switch (this->point_group_class) {
        case Class::C:
            return "C" + order;
        case Class::Ch:
            return "C" + order + "h";
        case Class::Cv:
            return "C" + order + "v";
        case Class::S:
            return "S" + order;
        case Class::D:
            return "D" + order;
        case Class::Dh:
            return "D" + order + "h";
        case Class::Dd:
            return "D" + order + "d";
        case Class::T:
            return "T";
        case Class::Td:
            return "Td";
        case Class::Th:
            return "Th";
        case Class::O:
            return "O";
        case Class::Oh:
            return "Oh";
        case Class::I:
            return "I";
        case Class::Ih:
            return "Ih";
        case Class::Cs:
            return "Cs";
        case Class::Ci:
            return "Ci";
        case Class::Cinfv:
            return "C∞v";
        case Class::Dinfh:
            return "D∞h";
        default:
            throw std::runtime_error("Unexpected point group class encountered.");
    }
}

/**
 * @brief Get the name of the point group in HTML formatting
 *
 * @return const std::string
 */
const std::string PointGroupLabel::get_name_html() const {
    std::string order = std::to_string(this->order);

    switch (this->point_group_class) {
        case Class::C:
            return "<i>C</i><sub>" + order + "</sub>";
        case Class::Ch:
            return "<i>C</i><sub>" + order + "h</sub>";
        case Class::Cv:
            return "<i>C</i><sub>" + order + "v</sub>";
        case Class::S:
            return "<i>S</i><sub>" + order + "</sub>";
        case Class::D:
            return "<i>D</i><sub>" + order + "</sub>";
        case Class::Dh:
            return "<i>D</i><sub>" + order + "h</sub>";
        case Class::Dd:
            return "<i>D</i><sub>" + order + "d</sub>";
        case Class::T:
            return "<i>T</i>";
        case Class::Td:
            return "<i>T</i><sub>d</sub>";
        case Class::Th:
            return "<i>T</i><sub>h</sub>";
        case Class::O:
            return "<i>O</i>";
        case Class::Oh:
            return "<i>O</i><sub>h</sub>";
        case Class::I:
            return "<i>I</i>";
        case Class::Ih:
            return "<i>I</i><sub>h</sub>";
        case Class::Cs:
            return "<i>C</i><sub>s</sub>";
        case Class::Ci:
            return "<i>C</i><sub>i</sub>";
        case Class::Cinfv:
            return "<i>C</i><sub>∞v</sub>";
        case Class::Dinfh:
            return "<i>D</i><sub>∞h</sub>";
        default:
            throw std::runtime_error("Unexpected point group class encountered.");
    }
}

/**
 * @brief Return whether the point group is a cyclic point group
 * (C, Ch, Cv, S)
 */
const bool PointGroupLabel::is_cyclic() const {
    return
        this->point_group_class == Class::C ||
        this->point_group_class == Class::Ch ||
        this->point_group_class == Class::Cv ||
        this->point_group_class == Class::S ||
        this->point_group_class == Class::Cs ||
        this->point_group_class == Class::Ci;
}

/**
 * @brief Return whether the point group is a dihedral point group
 * (D, Dh, Dd)
 */
const bool PointGroupLabel::is_dihedral() const {
    return
        this->point_group_class == Class::D ||
        this->point_group_class == Class::Dh ||
        this->point_group_class == Class::Dd;
}

/**
 * @brief Return whether the point group is polyhedral
 * (T, Td, Th, O, Oh, I, Ih)
 */
const bool PointGroupLabel::is_polyhedral() const {
    return
        this->point_group_class == Class::T ||
        this->point_group_class == Class::Td ||
        this->point_group_class == Class::Th ||
        this->point_group_class == Class::O ||
        this->point_group_class == Class::Oh ||
        this->point_group_class == Class::I ||
        this->point_group_class == Class::Ih;
}

/**
 * @brief Return whether the point group is tetrahedral (T, Td, Th)
 */
const bool PointGroupLabel::is_tetrahedral() const {
    return
        this->point_group_class == Class::T ||
        this->point_group_class == Class::Td ||
        this->point_group_class == Class::Th;
}

/**
 * @brief Return whether the point group is octahedral (O, Oh)
 */
const bool PointGroupLabel::is_octahedral() const {
    return this->point_group_class == Class::O || this->point_group_class == Class::Oh;
}

/**
 * @brief Return whether the point group is icosahedral (I, Ih)
 */
const bool PointGroupLabel::is_icosahedral() const {
    return this->point_group_class == Class::I || this->point_group_class == Class::Ih;
}

/**
 * @brief Return whether the point group is linear (C∞v, D∞h)
 */
const bool PointGroupLabel::is_linear() const {
    return this->point_group_class == Class::Cinfv || this->point_group_class == Class::Dinfh;
}

/**
 * @brief Check whether this symmetry operation matches another symmetry
 * operation
 *
 * This check does not take multiplicity into account.
 *
 * @param other other symmetry operation
 * @return true if operations match
 * @return false if operations don't match
 */
const bool PointGroupLabel::matches(PointGroupLabel& other) const {
    if (this->is_polyhedral()) {
        // classes without order
        return this->point_group_class == other.get_class();
    } else {
        return this->point_group_class == other.get_class() &&
            this->order == other.get_order();
    }
}

/**
 * @brief Mapping from string to point group class
 */
const std::unordered_map<std::string, PointGroupLabel::Class> PointGroupLabel::string_to_class = {
    {"C", Class::C},
    {"Ch", Class::Ch},
    {"Cv", Class::Cv},
    {"S", Class::S},
    {"D", Class::D},
    {"Dh", Class::Dh},
    {"Dd", Class::Dd},
    {"T", Class::T},
    {"Td", Class::Td},
    {"Th", Class::Th},
    {"O", Class::O},
    {"Oh", Class::Oh},
    {"I", Class::I},
    {"Ih", Class::Ih},
    {"Cs", Class::Cs},
    {"Ci", Class::Ci},
    {"Cinfv", Class::Cinfv},
    {"Dinfh", Class::Dinfh}
};

/**
 * @brief Get the point group class from a string representing the class
 *
 * @param class_string
 * @return Class
 */
PointGroupLabel::Class PointGroupLabel::get_class(std::string class_string) {
    std::unordered_map<std::string, Class>::const_iterator it =
        PointGroupLabel::string_to_class.find(class_string);

    if (it == PointGroupLabel::string_to_class.end()) {
        throw std::runtime_error("Invalid class encountered: " + class_string);
    }

    return it->second;
}
