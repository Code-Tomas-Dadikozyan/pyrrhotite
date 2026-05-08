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
#include <stdexcept>
#include <boost/test/unit_test.hpp>
#include "../src/orbitals/orbital_label.h"

BOOST_AUTO_TEST_SUITE(orbital_label);

BOOST_AUTO_TEST_CASE(create_valid) {
    OrbitalLabel one_s = OrbitalLabel(1, 0);
    OrbitalLabel two_s = OrbitalLabel(2, 0);
    OrbitalLabel two_p_y = OrbitalLabel(2, 1, -1);
    OrbitalLabel two_p_z = OrbitalLabel(2, 1, 0);
    OrbitalLabel two_p_x = OrbitalLabel(2, 1, 1);

    BOOST_TEST(one_s.get_principal() == 1);
    BOOST_TEST(one_s.get_azimuthal() == 0);

    BOOST_TEST(two_s.get_principal() == 2);
    BOOST_TEST(two_s.get_azimuthal() == 0);

    BOOST_TEST(two_p_y.get_principal() == 2);
    BOOST_TEST(two_p_y.get_azimuthal() == 1);
    BOOST_TEST(two_p_y.get_magnetic() == -1);

    BOOST_TEST(two_p_z.get_principal() == 2);
    BOOST_TEST(two_p_z.get_azimuthal() == 1);
    BOOST_TEST(two_p_z.get_magnetic() == 0);

    BOOST_TEST(two_p_x.get_principal() == 2);
    BOOST_TEST(two_p_x.get_azimuthal() == 1);
    BOOST_TEST(two_p_x.get_magnetic() == 1);
}

BOOST_AUTO_TEST_CASE(create_invalid) {
    BOOST_CHECK_THROW(OrbitalLabel a = OrbitalLabel(0, 0), std::runtime_error);
    BOOST_CHECK_THROW(OrbitalLabel b = OrbitalLabel(1, 1), std::runtime_error);
    BOOST_CHECK_THROW(OrbitalLabel c = OrbitalLabel(2, 2), std::runtime_error);
    BOOST_CHECK_THROW(OrbitalLabel d = OrbitalLabel(3, 0), std::runtime_error);
    BOOST_CHECK_THROW(OrbitalLabel e = OrbitalLabel(2, 0, 1), std::runtime_error);
    BOOST_CHECK_THROW(OrbitalLabel f = OrbitalLabel(2, 0, -1), std::runtime_error);
    BOOST_CHECK_THROW(OrbitalLabel g = OrbitalLabel(2, 1, 2), std::runtime_error);
    BOOST_CHECK_THROW(OrbitalLabel h = OrbitalLabel(2, 1, -2), std::runtime_error);
}

BOOST_AUTO_TEST_CASE(to_string) {
    OrbitalLabel one_s = OrbitalLabel(1, 0);
    OrbitalLabel two_s = OrbitalLabel(2, 0);
    OrbitalLabel two_p_y = OrbitalLabel(2, 1, -1);
    OrbitalLabel two_p_z = OrbitalLabel(2, 1, 0);
    OrbitalLabel two_p_x = OrbitalLabel(2, 1, 1);

    BOOST_TEST(one_s.get_name() == "1s");
    BOOST_TEST(two_s.get_name() == "2s");
    BOOST_TEST(two_p_y.get_name() == "2py");
    BOOST_TEST(two_p_z.get_name() == "2pz");
    BOOST_TEST(two_p_x.get_name() == "2px");

    BOOST_TEST(one_s.get_name_html() == "1s");
    BOOST_TEST(two_s.get_name_html() == "2s");
    BOOST_TEST(two_p_y.get_name_html() == "2p<sub><i>y</i></sub>");
    BOOST_TEST(two_p_z.get_name_html() == "2p<sub><i>z</i></sub>");
    BOOST_TEST(two_p_x.get_name_html() == "2p<sub><i>x</i></sub>");
}

BOOST_AUTO_TEST_CASE(create_from_string) {
    OrbitalLabel one_s = OrbitalLabel::get_orbital_label("1s");
    OrbitalLabel two_s = OrbitalLabel::get_orbital_label("2s");
    OrbitalLabel two_p_y = OrbitalLabel::get_orbital_label("2py");
    OrbitalLabel two_p_z = OrbitalLabel::get_orbital_label("2pz");
    OrbitalLabel two_p_x = OrbitalLabel::get_orbital_label("2px");

    BOOST_TEST(one_s.get_principal() == 1);
    BOOST_TEST(one_s.get_azimuthal() == 0);

    BOOST_TEST(two_s.get_principal() == 2);
    BOOST_TEST(two_s.get_azimuthal() == 0);

    BOOST_TEST(two_p_y.get_principal() == 2);
    BOOST_TEST(two_p_y.get_azimuthal() == 1);
    BOOST_TEST(two_p_y.get_magnetic() == -1);

    BOOST_TEST(two_p_z.get_principal() == 2);
    BOOST_TEST(two_p_z.get_azimuthal() == 1);
    BOOST_TEST(two_p_z.get_magnetic() == 0);

    BOOST_TEST(two_p_x.get_principal() == 2);
    BOOST_TEST(two_p_x.get_azimuthal() == 1);
    BOOST_TEST(two_p_x.get_magnetic() == 1);
}

BOOST_AUTO_TEST_SUITE_END();
