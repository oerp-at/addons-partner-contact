This is a glue module between the module **phone_validation** from the official addons and the OCA module **partner_mobile**.

Like Odoo does for **phone**, it adds the companion fields of the **mobile** number of partners: the phone widget displays the number in international format and dials it in E.164 format, while the raw value stays unchanged.

None of the two numbers is a main number: the phone widget of **phone** and **mobile** each displays and dials the number of its own field, also for SMS, WhatsApp and VoIP. Without this module, the phone widget of **phone** would display and dial the mobile number as soon as the partner has a valid mobile number.
