# -*- coding: utf-8 -*-

from odoo import tools
from odoo import api, fields, models


class StockMoveLineReport(models.Model):
    _name = "stock.move.line.report"
    _description = "Stock Move Line Report"
    _auto = False
    _rec_name = 'lote_number'
    _order = 'lote_number'

    lote_number = fields.Char('Lote Number', readonly=True)
    cat_cod = fields.Char('Category code', readonly=True)
    cat_name = fields.Char('Category name', readonly=True)
    rut = fields.Char('Rut', readonly=True)
    user_name = fields.Char('User name', readonly=True)
    at_marc_cod = fields.Integer('Marc code', readonly=True)
    at_marc_name = fields.Char('Marc name', readonly=True)
    at_model_name = fields.Char('Model name', readonly=True)
    provider_ref = fields.Char('Provider ref', readonly=True)
    at_processor_name = fields.Char('Processor name', readonly=True)
    at_speed_name = fields.Char('Speed name', readonly=True)
    at_memory_name = fields.Char('Memory name', readonly=True)
    at_hdd_name = fields.Char('HDD name', readonly=True)
    at_purchase_cost = fields.Integer('Purchase cost at', readonly=True)
    provider = fields.Char('Provider', readonly=True)
    invoice_n = fields.Integer('Invoice N', readonly=True)
    purchase_date = fields.Date('Purchase date', readonly=True)
    assignment_date = fields.Datetime('Assignment date', readonly=True)

    def _fnt_is_location_parent(self):
        psql = """
            CREATE OR REPLACE
            FUNCTION is_location_parent(loc_id integer) RETURNS boolean AS $$
            DECLARE
                is_parent boolean;
                parent_count integer;
            BEGIN
                SELECT SUM(id) INTO parent_count FROM stock_location WHERE location_id = loc_id;
                IF (parent_count > 0) THEN
                is_parent := TRUE;
                ELSE
                is_parent := FALSE;
                END IF;
                RETURN is_parent;
            END;
            $$ LANGUAGE plpgsql;        
        """
        self.env.cr.execute(psql)


    def _query(self):
        _select = """
            SELECT min(sml.id) as id, max(sml.date) AS assignment_date, spl.name AS lote_number, sl.name AS user_name, 
            spl.x_studio_n_factura AS invoice_n, spl.x_studio_costo_compra AS purchase_cost, 
            spl."x_studio_field_6Pp3S" AS purchase_date, spl.ref AS provider_ref,
            rp.name AS provider, po.date_order, pol.price_unit AS at_purchase_cost, pt.name AS product_name,
            at_marc.x_name AS at_marc_name, at_marc.x_cod_marcas_de_at AS at_marc_cod, 
            at_model.x_name AS at_model_name, at_memory.x_name AS at_memory_name, 
            at_hdd.x_name AS at_hdd_name, at_processor.x_name AS at_processor_name, 
            at_speed.x_name AS at_speed_name, pc.name AS cat_name, 
            pc."x_studio_field_B5Yrj" AS cat_cod, sl.barcode AS rut, sl.id AS sl_id

            FROM stock_move_line sml
            JOIN stock_production_lot spl ON sml.lot_id = spl.id
            JOIN product_product pp ON spl.product_id = pp.id
            JOIN product_template pt ON pp.product_tmpl_id = pt.id
            JOIN product_category pc ON pt.categ_id = pc.id
            JOIN stock_location sl ON sml.location_dest_id = sl.id
            JOIN stock_move sm ON sml.move_id = sm.id
            LEFT JOIN x_marcas_de_at at_marc ON pt."x_studio_field_To4X6" = at_marc.id 
            LEFT JOIN x_modelos_at at_model ON pt."x_studio_field_5Bj0L" = at_model.id
            LEFT JOIN x_memoria_at at_memory ON pt."x_studio_field_lNFQG" = at_memory.id
            LEFT JOIN x_hdd_at at_hdd ON pt."x_studio_field_WRME0" = at_hdd.id
            LEFT JOIN x_procesador_at at_processor ON pt."x_studio_field_E6Mvt" = at_processor.id
            LEFT JOIN x_velocidad_at at_speed ON pt."x_studio_field_q1N0G" = at_speed.id
            LEFT JOIN purchase_order_line pol ON sm.purchase_line_id = pol.id
            LEFT JOIN purchase_order po ON pol.order_id = po.id
            LEFT JOIN res_partner rp ON po.partner_id = rp.id

            GROUP BY 

            lote_number, user_name, invoice_n, purchase_cost, 
            purchase_date, provider_ref, provider, po.date_order, at_purchase_cost, product_name,
            at_marc_name, at_marc_cod, at_model_name, at_memory_name, at_hdd_name, at_processor_name, 
            at_speed_name, cat_name, cat_cod, rut, sl_id


            HAVING NOT is_location_parent(sl.id)
        """

        return _select

    @api.model_cr
    def init(self):
        self._fnt_is_location_parent()
        tools.drop_view_if_exists(self.env.cr, self._table)
        self.env.cr.execute("""CREATE or REPLACE VIEW %s as (%s)""" % (self._table, self._query()))