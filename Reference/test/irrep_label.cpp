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

#include <string>
#include <boost/test/unit_test.hpp>
#include "../src/symmetry/irreps/irrep_label.h"

BOOST_TEST_DONT_PRINT_LOG_VALUE(IrrepLabel::Mulliken);
BOOST_TEST_DONT_PRINT_LOG_VALUE(IrrepLabel::Parity);
BOOST_TEST_DONT_PRINT_LOG_VALUE(IrrepLabel::Prime);

BOOST_AUTO_TEST_SUITE(irrep_label);

BOOST_AUTO_TEST_CASE(mulliken) {
    IrrepLabel A = IrrepLabel(IrrepLabel::Mulliken::A);
    IrrepLabel B = IrrepLabel(IrrepLabel::Mulliken::B);

    BOOST_TEST(A.get_mulliken() == IrrepLabel::Mulliken::SingleSymmetric);
    BOOST_TEST(B.get_mulliken() == IrrepLabel::Mulliken::SingleAntisymmetric);

    BOOST_TEST(A.get_name() == "A");
    BOOST_TEST(A.get_name_html() == "A");
    BOOST_TEST(B.get_name() == "B");
    BOOST_TEST(B.get_name_html() == "B");
}

BOOST_AUTO_TEST_CASE(subscript) {
    IrrepLabel A1 = IrrepLabel(IrrepLabel::Mulliken::A, 1);

    BOOST_TEST(A1.get_subscript() == 1);

    BOOST_TEST(A1.get_name() == "A1");
    BOOST_TEST(A1.get_name_html() == "A<sub>1</sub>");
}

BOOST_AUTO_TEST_CASE(parity) {
    IrrepLabel Ag = IrrepLabel(IrrepLabel::Mulliken::A, IrrepLabel::Parity::g);

    BOOST_TEST(Ag.get_parity() == IrrepLabel::Parity::Gerade);

    BOOST_TEST(Ag.get_name() == "Ag");
    BOOST_TEST(Ag.get_name_html() == "A<sub>g</sub>");
}

BOOST_AUTO_TEST_CASE(prime) {
    IrrepLabel Ap = IrrepLabel(IrrepLabel::Mulliken::A, IrrepLabel::Prime::Single);

    BOOST_TEST(Ap.get_prime() == IrrepLabel::Prime::Single);

    BOOST_TEST(Ap.get_name() == "A\u2032");
    BOOST_TEST(Ap.get_name_html() == "A\u2032");
}

BOOST_AUTO_TEST_CASE(subscript_parity) {
    IrrepLabel A1g = IrrepLabel(IrrepLabel::Mulliken::A, 1, IrrepLabel::Parity::g);

    BOOST_TEST(A1g.get_subscript() == 1);
    BOOST_TEST(A1g.get_parity() == IrrepLabel::Parity::Gerade);

    BOOST_TEST(A1g.get_name() == "A1g");
    BOOST_TEST(A1g.get_name_html() == "A<sub>1g</sub>");
}

BOOST_AUTO_TEST_CASE(subscript_prime) {
    IrrepLabel A1p = IrrepLabel(IrrepLabel::Mulliken::A, 1, IrrepLabel::Prime::Single);

    BOOST_TEST(A1p.get_subscript() == 1);
    BOOST_TEST(A1p.get_prime() == IrrepLabel::Prime::Single);

    BOOST_TEST(A1p.get_name() == "A1\u2032");
    BOOST_TEST(A1p.get_name_html() == "A<sub>1</sub>\u2032");
}

BOOST_AUTO_TEST_SUITE_END();
