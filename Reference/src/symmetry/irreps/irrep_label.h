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

#ifndef SYMMETRY_IRREPS_IRREP_LABEL_H
#define SYMMETRY_IRREPS_IRREP_LABEL_H

#include <stdexcept>
#include <string>

class IrrepLabel {
public:
    enum class Mulliken : unsigned char {
        SingleSymmetric,
        SingleAntisymmetric,
        DoublyDegenerate,
        TriplyDegenerate,
        QuadruplyDegenerate,
        QuintuplyDegenerate,

        A = SingleSymmetric,
        B = SingleAntisymmetric,
        E = DoublyDegenerate,
        T = TriplyDegenerate,
        G = QuadruplyDegenerate,
        H = QuintuplyDegenerate
    };

    enum class Parity : unsigned char {
        None,
        Gerade,
        Ungerade,

        g = Gerade,
        u = Ungerade
    };

    enum class Prime : unsigned char {
        None,
        Single,
        Double
    };

private:
    Mulliken mulliken;
    unsigned int subscript;
    Parity parity;
    Prime prime;

public:
    /**
     * @brief Default constructor
     */
    IrrepLabel();

    /**
     * @brief Construct a new Irrep Label object
     *
     * @param mulliken Mulliken symbol
     * @param subscript integer subscript
     * @param parity symmetry with respect to a center of inversion
     * @param prime symmetry with respect to a horizontal mirror plane
     */
    IrrepLabel(Mulliken mulliken, unsigned int subscript, Parity parity, Prime prime);

    /**
     * @brief Construct a new Irrep Label object
     *
     * @param mulliken Mulliken symbol
     */
    IrrepLabel(Mulliken mulliken);

    /**
     * @brief Construct a new Irrep Label object
     *
     * @param mulliken Mulliken symbol
     * @param subscript integer subscript
     */
    IrrepLabel(Mulliken mulliken, unsigned int subscript);

    /**
     * @brief Construct a new Irrep Label object
     *
     * @param mulliken Mulliken symbol
     * @param parity symmetry with respect to a center of inversion
     */
    IrrepLabel(Mulliken mulliken, Parity parity);

    /**
     * @brief Construct a new Irrep Label object
     *
     * @param mulliken Mulliken symbol
     * @param subscript integer subscript
     * @param parity symmetry with respect to a center of inversion
     */
    IrrepLabel(Mulliken mulliken, unsigned int subscript, Parity parity);

    /**
     * @brief Construct a new Irrep Label object
     *
     * @param mulliken Mulliken symbol
     * @param prime symmetry with respect to a horizontal mirror plane
     */
    IrrepLabel(Mulliken mulliken, Prime prime);

    /**
     * @brief Construct a new Irrep Label object
     *
     * @param mulliken Mulliken symbol
     * @param subscript integer subscript
     * @param prime symmetry with respect to a horizontal mirror plane
     */
    IrrepLabel(Mulliken mulliken, unsigned int subscript, Prime prime);

    /**
     * @brief Get the Mulliken symbol of this irreducible representation
     *
     * @return const Mulliken
     */
    const Mulliken get_mulliken() const;

    /**
     * @brief Get the integer subscript of this irreducible representation
     *
     * @return const unsigned int
     */
    const unsigned int get_subscript() const;

    /**
     * @brief Get the parity of this irreducible representation
     *
     * @return const Parity
     */
    const Parity get_parity() const;

    /**
     * @brief Get the prime of this irreducible representation
     *
     * @return const Prime
     */
    const Prime get_prime() const;

    /**
     * @brief Get the name of this irreducible representation in plaintext
     *
     * @return const std::string
     */
    const std::string get_name() const;

    /**
     * @brief Get the name of this irreducible representation in HTML
     * formatting
     *
     * @return const std::string
     */
    const std::string get_name_html() const;
};

#endif  // SYMMETRY_IRREPS_IRREP_LABEL_H
