/* poppler-python: python binding to the poppler-cpp pdf lib
 * Copyright (C) 2020, Charles Brunet <charles@cbrunet.net>
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License along
 * with this program; if not, write to the Free Software Foundation, Inc.,
 * 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
 */

#include <pybind11/pybind11.h>
#include <poppler/cpp/poppler-global.h>

namespace py = pybind11;

namespace poppler
{

    std::string from_ustring(poppler::ustring str)
    {
        auto a = str.to_utf8();
        return std::string(a.begin(), a.end());
    }

    poppler::ustring to_ustring(std::string str)
    {
        return poppler::ustring::from_utf8(str.data(), str.size());
    }


PYBIND11_MODULE(_global, m)
{
    py::enum_<permission_enum>(m, "permission_enum")
        .value("print", permission_enum::perm_print)
        .value("change", permission_enum::perm_change)
        .value("copy", permission_enum::perm_copy)
        .value("add_notes", permission_enum::perm_add_notes)
        .value("fill_forms", permission_enum::perm_fill_forms)
        .value("accessibility", permission_enum::perm_accessibility)
        .value("assemble", permission_enum::perm_assemble)
        .value("print_high_resolution", permission_enum::perm_print_high_resolution)
        .export_values();

    py::enum_<page_box_enum>(m, "page_box_enum")
        .value("media_box", page_box_enum::media_box)
        .value("crop_box", page_box_enum::crop_box)
        .value("bleed_box", page_box_enum::bleed_box)
        .value("trim_box", page_box_enum::trim_box)
        .value("art_box", page_box_enum::art_box)
        .export_values();

    py::enum_<rotation_enum>(m, "rotation_enum")
        .value("rotate_0", rotation_enum::rotate_0)
        .value("rotate_90", rotation_enum::rotate_90)
        .value("rotate18_0", rotation_enum::rotate_180)
        .value("rotate27_0", rotation_enum::rotate_270)
        .export_values();

    py::class_<ustring>(m, "_ustring")
        .def("__str__", &from_ustring)
        ;

    m.def("ustring", &to_ustring);
}

} // namespace poppler