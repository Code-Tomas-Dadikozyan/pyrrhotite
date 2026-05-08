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

#include "file.h"

/**
 * @brief Construct a new File object
 *
 * @param path name of the file
 */
File::File(const std::string path) {
    if (path[0] == ':') {
        this->read_qt_resource(path);
    } else {
        this->read_from_disk(path);
    }
}

/**
 * @brief Get the stream object
 *
 * @return std::stringstream&
 */
std::stringstream& File::get_stream() {
    return this->stream;
}

/**
 * @brief Get the source of the file
 *
 * @return Source
 */
File::Source File::get_source() {
    return this->source;
}

/**
 * @brief Read file from disk
 *
 * @param path name of the file
 */
void File::read_from_disk(const std::string& path) {
    this->source = Source::Disk;

    std::ifstream ifs(path);
    if (!ifs.is_open()) {
        throw std::runtime_error("Could not open file: " + path);
    }

    this->stream << ifs.rdbuf();
}

/**
 * @brief Read file from the Qt resource system
 *
 * @param path name of the file
 */
void File::read_qt_resource(const std::string& path) {
    this->source = Source::QtResource;

    QFile file(QString::fromStdString(path));
    if (!file.open(QIODevice::ReadOnly)) {
        throw std::runtime_error("Could not open file: " + path);
    }

    QByteArray ba = file.readAll();
    file.close();

    this->stream << ba.toStdString();
}
