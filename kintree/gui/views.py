import flet as ft
from flet import View

# InvenTree
from ..database import inventree_interface
# Tools
from ..common.tools import cprint, create_library

# Navigation indexes
NAV_BAR_INDEX = {
    0: '/search',
    1: '/kicad',
    2: '/inventree',
}

# TODO: replace with settings
SUPPORTED_SUPPLIERS = [
    'Digi-Key',
    'Mouser',
    'Farnell',
    'Newark',
    'Element14',
    'LCSC',
]

appbar = ft.AppBar(
    leading=ft.Icon(ft.icons.INVENTORY),
    leading_width=40,
    title=ft.Text('Ki-nTree | 0.7.0dev'),
    center_title=False,
    bgcolor=ft.colors.SURFACE_VARIANT,
    actions=[],
)

navrail = ft.NavigationRail(
    selected_index=0,
    label_type=ft.NavigationRailLabelType.ALL,
    min_width=100,
    min_extended_width=400,
    group_alignment=-0.9,
    destinations=[
        ft.NavigationRailDestination(
            icon=ft.icons.SEARCH,
            selected_icon=ft.icons.MANAGE_SEARCH,
            label="Search"
        ),
        ft.NavigationRailDestination(
            icon=ft.icons.SETTINGS_INPUT_COMPONENT_OUTLINED,
            selected_icon=ft.icons.SETTINGS_INPUT_COMPONENT,
            label="KiCad",
        ),
        ft.NavigationRailDestination(
            icon=ft.icons.INVENTORY_2_OUTLINED,
            selected_icon_content=ft.Icon(ft.icons.INVENTORY),
            label="InvenTree",
        ),
    ],
    on_change=None,
)


class SettingsView(View):
    '''Settings view'''

    route = '/settings'
    __appbar = ft.AppBar(title=ft.Text('User Settings'), bgcolor=ft.colors.SURFACE_VARIANT)

    def __init__(self, page: ft.Page):
        route = self.route
        super().__init__(route=route)
        self.controls = [
            self.__appbar,
            ft.Text('Settings View', style="bodyMedium"),
        ]


class MainView(View):
    '''Common main view'''

    navidx = None
    route = '/'
    page = None
    column = None
    fields = {}

    def __init__(self, page: ft.Page):
        # Store page pointer
        self.page = page

        # Set route
        if self.navidx is not None:
            self.route = NAV_BAR_INDEX[self.navidx]

        # Init view
        super().__init__(route=self.route)

        # Set appbar
        if not appbar.actions:
            appbar.actions.append(ft.IconButton(ft.icons.SETTINGS, on_click=lambda e: self.page.go('/settings')))
        self.appbar = appbar

        # Set navigation rail
        if not navrail.on_change:
            navrail.on_change = lambda e: self.page.go(NAV_BAR_INDEX[e.control.selected_index])
        self.__navigation_bar = navrail

        # Build column
        self.column = self.build_column()

        # Build controls
        self.controls = self.build_controls()

    def build_column():
        # Empty column (to be set inside the children views)
        return ft.Column()

    def build_controls(self):
        return [
            ft.Row(
                controls=[
                    self.__navigation_bar,
                    ft.VerticalDivider(width=1),
                    self.column,
                ],
                expand=True,
            ),
        ]


class SearchView(MainView):
    '''Search view'''

    navidx = 0

    # List of search fields
    search_fields_list = [
        'name',
        'description',
        'revision',
        'keywords',
        'supplier_name',
        'supplier_part_number',
        'supplier_link',
        'manufacturer_name',
        'manufacturer_part_number',
        'datasheet',
        'image',
    ]

    fields = {
        'part_number': ft.TextField(label="Part Number", hint_text="Part Number", width=300, expand=True),
        'supplier': ft.Dropdown(label="Supplier"),
        'search_form': {},
    }

    def __init__(self, page: ft.Page):
        # Init view
        super().__init__(page)

        # Populate dropdown suppliers
        self.fields['supplier'].options = [ft.dropdown.Option(supplier) for supplier in SUPPORTED_SUPPLIERS]

        # Create search form
        for field in self.search_fields_list:
            label = field.replace('_', ' ').title()
            text_field = ft.TextField(label=label, hint_text=label, disabled=True, expand=True)
            self.column.controls.append(ft.Row(controls=[text_field]))
            self.fields['search_form'][field] = text_field

    def search_enable_fields(self):
        for form_field in self.fields['search_form'].values():
            form_field.disabled = False
        self.page.update()
        return

    def run_search(self):
        self.page.splash.visible = True
        self.page.update()

        if not self.fields['part_number'].value and not self.fields['supplier'].value:
            self.search_enable_fields()
        else:
            # Supplier search
            part_supplier_info = inventree_interface.supplier_search(self.fields['supplier'].value, self.fields['part_number'].value)

            if part_supplier_info:
                # Translate to user form format
                part_supplier_form = inventree_interface.translate_supplier_to_form(supplier=self.fields['supplier'].value,
                                           part_info=part_supplier_info)

            if part_supplier_info:
                for field_idx, field_name in enumerate(self.fields['search_form'].keys()):
                    # print(field_idx, field_name, get_default_search_keys()[field_idx], search_form_field[field_name])
                    try:
                        self.fields['search_form'][field_name].value = part_supplier_form.get(field_name, '')
                    except IndexError:
                        pass
                    # Enable editing
                    self.fields['search_form'][field_name].disabled = False

        self.page.splash.visible = False
        self.page.update()
        return

    def build_column(self):
        return ft.Column(
            controls=[
                ft.Row(),
                ft.Row(
                    controls=[
                        self.fields['part_number'],
                        self.fields['supplier'],
                        ft.FloatingActionButton(
                            icon=ft.icons.SEARCH,
                            on_click=lambda e: self.run_search(),
                        ),
                    ],
                ),
                ft.Divider(),
            ],
            alignment=ft.MainAxisAlignment.START,
            scroll=ft.ScrollMode.HIDDEN,
            expand=True,
        )


class KicadView(MainView):
    '''KiCad view'''

    navidx = 1

    def build_column(self):
        return ft.Column(
            controls=[
                ft.Text('KiCad', style="bodyMedium"),
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True,
        )


class InvenTreeView(MainView):
    '''InvenTree view'''

    navidx = 2

    def build_column(self):
        return ft.Column(
            controls=[
                ft.Text('InvenTree', style="bodyMedium"),
            ],
            alignment=ft.MainAxisAlignment.START,
            expand=True,
        )
