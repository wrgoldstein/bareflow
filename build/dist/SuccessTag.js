/* src/SuccessTag.svelte generated by Svelte v3.31.2 */
import {
	SvelteComponent,
	append,
	attr,
	create_slot,
	detach,
	element,
	init,
	insert,
	safe_not_equal,
	space,
	svg_element,
	transition_in,
	transition_out,
	update_slot
} from "../web_modules/svelte/internal.js";

function create_fragment(ctx) {
	let span;
	let div;
	let svg;
	let path;
	let t;
	let current;
	const default_slot_template = /*#slots*/ ctx[1].default;
	const default_slot = create_slot(default_slot_template, ctx, /*$$scope*/ ctx[0], null);

	return {
		c() {
			span = element("span");
			div = element("div");
			svg = svg_element("svg");
			path = svg_element("path");
			t = space();
			if (default_slot) default_slot.c();
			attr(path, "fill-rule", "evenodd");
			attr(path, "d", "M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0\n            011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z");
			attr(path, "clip-rule", "evenodd");
			attr(svg, "class", "-ml-1 mr-2 h-5 w-5");
			attr(svg, "xmlns", "http://www.w3.org/2000/svg");
			attr(svg, "viewBox", "0 0 20 20");
			attr(svg, "fill", "currentColor");
			attr(svg, "aria-hidden", "true");
			attr(div, "class", "inline-flex items-center px-4 py-2 border border-transparent\n      rounded shadow-sm text-sm font-medium text-white bg-green-600");
			attr(span, "class", "sm:ml-3");
		},
		m(target, anchor) {
			insert(target, span, anchor);
			append(span, div);
			append(div, svg);
			append(svg, path);
			append(div, t);

			if (default_slot) {
				default_slot.m(div, null);
			}

			current = true;
		},
		p(ctx, [dirty]) {
			if (default_slot) {
				if (default_slot.p && dirty & /*$$scope*/ 1) {
					update_slot(default_slot, default_slot_template, ctx, /*$$scope*/ ctx[0], dirty, null, null);
				}
			}
		},
		i(local) {
			if (current) return;
			transition_in(default_slot, local);
			current = true;
		},
		o(local) {
			transition_out(default_slot, local);
			current = false;
		},
		d(detaching) {
			if (detaching) detach(span);
			if (default_slot) default_slot.d(detaching);
		}
	};
}

function instance($$self, $$props, $$invalidate) {
	let { $$slots: slots = {}, $$scope } = $$props;

	$$self.$$set = $$props => {
		if ("$$scope" in $$props) $$invalidate(0, $$scope = $$props.$$scope);
	};

	return [$$scope, slots];
}

class SuccessTag extends SvelteComponent {
	constructor(options) {
		super();
		init(this, options, instance, create_fragment, safe_not_equal, {});
	}
}

export default SuccessTag;