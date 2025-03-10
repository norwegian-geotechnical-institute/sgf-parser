import re
from typing import TextIO, Any

from sgf_parser.models.method import Method, MethodData
from sgf_parser import models
from sgf_parser.models import ParseState

# Fields are generally separated by "," and contain a single "="
# separating the key from the value. However, some fields have values
# containing ",", with no quoting. To handle this, we require the key
# to contain only a-z and A-Z. In addition, the Geotech AB extension,
# have date fields (key "%") with no "=" separating the key from the
# value...
_RE_FIELD_SEP = re.compile(r",(?=[a-zA-Z%])")


class Parser:
    """
    A class to parse an SGF file
    """

    method_code_class_mapping = {
        "2": models.MethodWST,
        "07": models.MethodCPT,
        "10": models.MethodSLB,
        "101": models.MethodWST,
        "102": models.MethodWST,
        "107A": models.MethodCPT,
        "107B": models.MethodCPT,
        "108A": models.MethodDP,
        "108B": models.MethodDP,
        "108C": models.MethodDP,
        "108D": models.MethodDP,
        "108E": models.MethodDP,
        "11": models.MethodSTI,
        "12": models.MethodSRS,
        "13": models.MethodSVT,
        "23": models.MethodRP,
        "24": models.MethodTOT,
        "3": models.MethodTR,
        "35": models.MethodDT,
        "41": models.MethodSRS,
        "42": models.MethodSRS,
        "7": models.MethodCPT,
        "71": models.MethodSRS,
        "72": models.MethodSRS,
        "73": models.MethodSRS,
        "8": models.MethodDP,
        "9": models.MethodDP,
    }

    def parse(self, file: TextIO) -> list[Method]:
        """
        Parse the SGF file

        The file parameter must be an opened file in text mode (with correct character encoding), pointing at the start
        of the file to parse. The file pointer may not point at the end of the file when this method returns.
        """

        blocks = {
            "£": ParseState.METHOD,
            "$": ParseState.HEADER,
            "#": ParseState.DATA,
            "€": ParseState.METHOD,
            "#$": ParseState.QUIT,
        }
        methods: list[Method] = []
        method: Method | None = None
        header: dict[str, Any] = {}

        state = None
        for row in file:
            row = row.rstrip()
            if not row:
                continue

            # Possible state changes
            if row in blocks:
                _new_state = blocks[row]
                _old_state = state
                if _new_state == ParseState.DATA and state in (ParseState.HEADER, ParseState.METHOD):
                    # Starting a new data block, so store the current collected header in a new method
                    method = self.parse_header(header)
                    header = {}
                elif _new_state in (ParseState.HEADER, ParseState.METHOD) and _old_state == ParseState.DATA:
                    # Finished populating current method, since new method is starting
                    # Store the current method, and empty the current method
                    if method:
                        methods.append(method)
                    else:
                        raise Exception("Method is None, that is unexpected")
                    method = None
                state = _new_state
                continue

            match state:
                case ParseState.HEADER | ParseState.METHOD:
                    header |= self._convert_str_to_dict(row)
                case ParseState.DATA:
                    if not method:
                        raise ValueError("No method to add data to")
                    method.method_data.append(self.parse_data(method, row))
                case ParseState.QUIT:
                    break
                case None:
                    raise ValueError("First block is not a main block")

        if method:
            method.post_processing()
            methods.append(method)

        return methods

    @staticmethod
    def _convert_str_to_dict(line: str) -> dict[str, Any]:
        """
        Convert row to dict. If repeated keys, then append values with ", " (comma and a space) as a separator
        """
        line = line.rstrip(",")
        result: dict[str, Any] = {}
        for k, v in (i.split("=", 1) if "=" in i else [i[0], i[1:]] for i in re.split(_RE_FIELD_SEP, line) if i):
            if not v:
                continue
            if k in result:
                result[k] += f", {v}"
            else:
                result[k] = v
        return result

    def parse_header(self, header: dict[str, Any]) -> Method:
        """
        When finished collecting the header dict, then create the Method object
        """
        if "HM" not in header:
            raise ValueError("Header does not contain a HM field")

        if header["HM"] not in self.method_code_class_mapping:
            raise ValueError(f"Unsupported value in the HM field {header['HM']!r}")

        return self.method_code_class_mapping[header["HM"]].model_validate(header)

    def parse_data(self, method: Method, row: str) -> MethodData:
        row_dict = self._convert_str_to_dict(row)
        method_data = method.method_data_type.model_validate(row_dict)
        return method_data
