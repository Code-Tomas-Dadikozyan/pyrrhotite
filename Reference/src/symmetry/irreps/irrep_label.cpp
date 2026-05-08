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

#include "irrep_label.h"

/**
 * @brief Default constructor
 */
IrrepLabel::IrrepLabel() {}

/**
 * @brief Construct a new Irrep Label object
 *
 * @param mulliken Mulliken symbol
 * @param subscript integer subscript
 * @param parity symmetry with respect to a center of inversion
 * @param prime symmetry with respect to a horizontal mirror plane
 */
IrrepLabel::IrrepLabel(Mulliken mulliken, unsigned int subscript, Parity parity, Prime prime) {
    this->mulliken = mulliken;
    this->subscript = subscript;
    this->parity = parity;
    this->prime = prime;
}

/**
 * @brief Construct a new Irrep Label object
 *
 * @param mulliken Mulliken symbol
 */
IrrepLabel::IrrepLabel(Mulliken mulliken) {
    this->mulliken = mulliken;
    this->subscript = 0;
    this->parity = Parity::None;
    this->prime = Prime::None;
}

/**
 * @brief Construct a new Irrep Label object
 *
 * @param mulliken Mulliken symbol
 * @param subscript integer subscript
 */
IrrepLabel::IrrepLabel(Mulliken mulliken, unsigned int subscript) {
    this->mulliken = mulliken;
    this->subscript = subscript;
    this->parity = Parity::None;
    this->prime = Prime::None;
}

/**
 * @brief Construct a new Irrep Label object
 *
 * @param mulliken Mulliken symbol
 * @param parity symmetry with respect to a center of inversion
 */
IrrepLabel::IrrepLabel(Mulliken mulliken, Parity parity) {
    this->mulliken = mulliken;
    this->subscript = 0;
    this->parity = parity;
    this->prime = Prime::None;
}

/**
 * @brief Construct a new Irrep Label object
 *
 * @param mulliken Mulliken symbol
 * @param subscript integer subscript
 * @param parity symmetry with respect to a center of inversion
 */
IrrepLabel::IrrepLabel(Mulliken mulliken, unsigned int subscript, Parity parity) {
    this->mulliken = mulliken;
    this->subscript = subscript;
    this->parity = parity;
    this->prime = Prime::None;
}

/**
 * @brief Construct a new Irrep Label object
 *
 * @param mulliken Mulliken symbol
 * @param prime symmetry with respect to a horizontal mirror plane
 */
IrrepLabel::IrrepLabel(Mulliken mulliken, Prime prime) {
    this->mulliken = mulliken;
    this->subscript = 0;
    this->parity = Parity::None;
    this->prime = prime;
}

/**
 * @brief Construct a new Irrep Label object
 *
 * @param mulliken Mulliken symbol
 * @param subscript integer subscript
 * @param prime symmetry with respect to a horizontal mirror plane
 */
IrrepLabel::IrrepLabel(Mulliken mulliken, unsigned int subscript, Prime prime) {
    this->mulliken = mulliken;
    this->subscript = subscript;
    this->parity = Parity::None;
    this->prime = prime;
}

/**
 * @brief Get the Mulliken symbol of this irreducible representation
 *
 * @return const Mulliken
 */
const IrrepLabel::Mulliken IrrepLabel::get_mulliken() const {
    return this->mulliken;
}

/**
 * @brief Get the integer subscript of this irreducible representation
 *
 * @return const unsigned int
 */
const unsigned int IrrepLabel::get_subscript() const {
    return this->subscript;
}

/**
 * @brief Get the parity of this irreducible representation
 *
 * @return const Parity
 */
const IrrepLabel::Parity IrrepLabel::get_parity() const {
    return this->parity;
}

/**
 * @brief Get the prime of this irreducible representation
 *
 * @return const Prime
 */
const IrrepLabel::Prime IrrepLabel::get_prime() const {
    return this->prime;
}

/**
 * @brief Get the name of this irreducible representation in plaintext
 *
 * @return const std::string
 */
const std::string IrrepLabel::get_name() const {
    std::string name;

    switch (this->mulliken) {
        case Mulliken::SingleSymmetric:
            name += "A";
            break;
        case Mulliken::SingleAntisymmetric:
            name += "B";
            break;
        case Mulliken::DoublyDegenerate:
            name += "E";
            break;
        case Mulliken::TriplyDegenerate:
            name += "T";
            break;
        case Mulliken::QuadruplyDegenerate:
            name += "G";
            break;
        case Mulliken::QuintuplyDegenerate:
            name += "H";
            break;
        default:
            throw std::runtime_error("Unexpected Mulliken symbol encountered.");
    }

    if (this->subscript > 0) name += std::to_string(this->subscript);

    if (this->parity != Parity::None) {
        switch (this->parity) {
            case Parity::Gerade:
                name += "g";
                break;
            case Parity::Ungerade:
                name += "u";
                break;
            default:
                throw std::runtime_error("Unexpected parity encountered.");
        }
    }

    if (this->prime != Prime::None) {
        switch (this->prime) {
            case Prime::Single:
                name += "\u2032";
                break;
            case Prime::Double:
                name += "\u2033";
                break;
            default:
                throw std::runtime_error("Unexpected prime encountered.");
        }
    }

    return name;
}

/**
 * @brief Get the name of this irreducible representation in HTML
 * formatting
 *
 * @return const std::string
 */
const std::string IrrepLabel::get_name_html() const {
    std::string name;

    switch (this->mulliken) {
        case Mulliken::SingleSymmetric:
            name += "A";
            break;
        case Mulliken::SingleAntisymmetric:
            name += "B";
            break;
        case Mulliken::DoublyDegenerate:
            name += "E";
            break;
        case Mulliken::TriplyDegenerate:
            name += "T";
            break;
        case Mulliken::QuadruplyDegenerate:
            name += "G";
            break;
        case Mulliken::QuintuplyDegenerate:
            name += "H";
            break;
        default:
            throw std::runtime_error("Unexpected Mulliken symbol encountered.");
    }

    std::string subscript_str;

    if (this->subscript > 0) subscript_str += std::to_string(this->subscript);

    if (this->parity != Parity::None) {
        switch (this->parity) {
            case Parity::Gerade:
                subscript_str += "g";
                break;
            case Parity::Ungerade:
                subscript_str += "u";
                break;
            default:
                throw std::runtime_error("Unexpected parity encountered.");
        }
    }

    if (!subscript_str.empty()) name += "<sub>" + subscript_str + "</sub>";

    if (this->prime != Prime::None) {
        switch (this->prime) {
            case Prime::Single:
                name += "\u2032";
                break;
            case Prime::Double:
                name += "\u2033";
                break;
            default:
                throw std::runtime_error("Unexpected prime encountered.");
        }
    }

    return name;
}
