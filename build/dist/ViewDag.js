/* src/ViewDag.svelte generated by Svelte v3.31.2 */
import {
	SvelteComponent,
	append,
	attr,
	component_subscribe,
	detach,
	element,
	empty,
	init,
	insert,
	listen,
	noop,
	safe_not_equal,
	set_data,
	space,
	svg_element,
	text
} from "../web_modules/svelte/internal.js";

import { dag, dag_id } from "./stores.js";

function create_else_block(ctx) {
	let t;

	return {
		c() {
			t = text("loading");
		},
		m(target, anchor) {
			insert(target, t, anchor);
		},
		p: noop,
		d(detaching) {
			if (detaching) detach(t);
		}
	};
}

// (30:0) {#if $dag}
function create_if_block(ctx) {
	let div5;
	let div3;
	let h2;
	let t0;
	let t1;
	let div2;
	let div0;
	let svg0;
	let path0;
	let t2;
	let t3_value = /*$dag*/ ctx[2].schedule + "";
	let t3;
	let t4;
	let div1;
	let svg1;
	let path1;
	let t5;
	let t6_value = /*$dag*/ ctx[2].image + "";
	let t6;
	let t7;
	let div4;
	let span0;
	let t9;
	let span1;
	let t11;
	let span2;
	let button2;
	let t13;
	let span3;
	let t15;
	let div8;
	let div7;
	let div6;
	let span4;
	let t16;
	let pre;
	let t17;
	let mounted;
	let dispose;
	let if_block = /*pod*/ ctx[3] && create_if_block_1(ctx);

	return {
		c() {
			div5 = element("div");
			div3 = element("div");
			h2 = element("h2");
			t0 = text(/*$dag_id*/ ctx[1]);
			t1 = space();
			div2 = element("div");
			div0 = element("div");
			svg0 = svg_element("svg");
			path0 = svg_element("path");
			t2 = space();
			t3 = text(t3_value);
			t4 = space();
			div1 = element("div");
			svg1 = svg_element("svg");
			path1 = svg_element("path");
			t5 = space();
			t6 = text(t6_value);
			t7 = space();
			div4 = element("div");
			span0 = element("span");

			span0.innerHTML = `<button type="button" class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"><svg class="-ml-1 mr-2 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path d="M13.586 3.586a2 2 0 112.828 2.828l-.793.793-2.828-2.828.793-.793zM11.379 5.793L3 14.172V17h2.828l8.38-8.379-2.83-2.828z"></path></svg>
            Edit</button>`;

			t9 = space();
			span1 = element("span");

			span1.innerHTML = `<button type="button" class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"><svg class="-ml-1 mr-2 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M12.586 4.586a2 2 0 112.828 2.828l-3 3a2 2 0 01-2.828 0 1 1 0 00-1.414 1.414 4 4 0 005.656 0l3-3a4 4 0 00-5.656-5.656l-1.5 1.5a1 1 0 101.414 1.414l1.5-1.5zm-5 5a2 2 0 012.828 0 1 1 0 101.414-1.414 4 4 0 00-5.656 0l-3 3a4 4 0 105.656 5.656l1.5-1.5a1 1 0 10-1.414-1.414l-1.5 1.5a2 2 0 11-2.828-2.828l3-3z" clip-rule="evenodd"></path></svg>
            View</button>`;

			t11 = space();
			span2 = element("span");
			button2 = element("button");

			button2.innerHTML = `<svg class="-ml-1 mr-2 h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd"></path></svg>
            Run`;

			t13 = space();
			span3 = element("span");

			span3.innerHTML = `<button type="button" class="inline-flex items-center px-4 py-2 border border-gray-300 rounded-md shadow-sm text-sm font-medium text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500" id="mobile-menu" aria-haspopup="true">More
            
            <svg class="-mr-1 ml-2 h-5 w-5 text-gray-500" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true"><path fill-rule="evenodd" d="M5.293 7.293a1 1 0 011.414 0L10 10.586l3.293-3.293a1 1 0 111.414 1.414l-4 4a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414z" clip-rule="evenodd"></path></svg></button>`;

			t15 = space();
			div8 = element("div");
			div7 = element("div");
			div6 = element("div");
			span4 = element("span");
			if (if_block) if_block.c();
			t16 = space();
			pre = element("pre");
			t17 = text(/*logs*/ ctx[0]);
			attr(h2, "class", "text-2xl font-bold leading-7 text-gray-900 sm:text-3xl sm:truncate");
			attr(path0, "fill-rule", "evenodd");
			attr(path0, "d", "M6 2a1 1 0 00-1 1v1H4a2 2 0 00-2 2v10a2 2 0 002 2h12a2 2 0 002-2V6a2 2 0 00-2-2h-1V3a1 1 0 10-2 0v1H7V3a1 1 0 00-1-1zm0 5a1 1 0 000 2h8a1 1 0 100-2H6z");
			attr(path0, "clip-rule", "evenodd");
			attr(svg0, "class", "flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400");
			attr(svg0, "xmlns", "http://www.w3.org/2000/svg");
			attr(svg0, "viewBox", "0 0 20 20");
			attr(svg0, "fill", "currentColor");
			attr(svg0, "aria-hidden", "true");
			attr(div0, "class", "mt-2 flex items-center text-sm text-gray-500");
			attr(path1, "d", "M13.983 11.078h2.119a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.119a.185.185 0 00-.185.185v1.888c0 .102.083.185.185.185m-2.954-5.43h2.118a.186.186 0 00.186-.186V3.574a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.185m0 2.716h2.118a.187.187 0 00.186-.186V6.29a.186.186 0 00-.186-.185h-2.118a.185.185 0 00-.185.185v1.887c0 .102.082.185.185.186m-2.93 0h2.12a.186.186 0 00.184-.186V6.29a.185.185 0 00-.185-.185H8.1a.185.185 0 00-.185.185v1.887c0 .102.083.185.185.186m-2.964 0h2.119a.186.186 0 00.185-.186V6.29a.185.185 0 00-.185-.185H5.136a.186.186 0 00-.186.185v1.887c0 .102.084.185.186.186m5.893 2.715h2.118a.186.186 0 00.186-.185V9.006a.186.186 0 00-.186-.186h-2.118a.185.185 0 00-.185.185v1.888c0 .102.082.185.185.185m-2.93 0h2.12a.185.185 0 00.184-.185V9.006a.185.185 0 00-.184-.186h-2.12a.185.185 0 00-.184.185v1.888c0 .102.083.185.185.185m-2.964 0h2.119a.185.185 0 00.185-.185V9.006a.185.185 0 00-.184-.186h-2.12a.186.186 0 00-.186.186v1.887c0 .102.084.185.186.185m-2.92 0h2.12a.185.185 0 00.184-.185V9.006a.185.185 0 00-.184-.186h-2.12a.185.185 0 00-.184.185v1.888c0 .102.082.185.185.185M23.763 9.89c-.065-.051-.672-.51-1.954-.51-.338.001-.676.03-1.01.087-.248-1.7-1.653-2.53-1.716-2.566l-.344-.199-.226.327c-.284.438-.49.922-.612 1.43-.23.97-.09 1.882.403 2.661-.595.332-1.55.413-1.744.42H.751a.751.751 0 00-.75.748 11.376 11.376 0 00.692 4.062c.545 1.428 1.355 2.48 2.41 3.124 1.18.723 3.1 1.137 5.275 1.137.983.003 1.963-.086 2.93-.266a12.248 12.248 0 003.823-1.389c.98-.567 1.86-1.288 2.61-2.136 1.252-1.418 1.998-2.997 2.553-4.4h.221c1.372 0 2.215-.549 2.68-1.009.309-.293.55-.65.707-1.046l.098-.288Z");
			attr(svg1, "class", "flex-shrink-0 mr-1.5 h-5 w-5 text-gray-400");
			attr(svg1, "xmlns", "http://www.w3.org/2000/svg");
			attr(svg1, "viewBox", "0 0 24 24");
			attr(svg1, "fill", "currentColor");
			attr(svg1, "aria-hidden", "true");
			attr(div1, "class", "mt-2 flex items-center text-sm text-gray-500");
			attr(div2, "class", "mt-1 flex flex-col sm:flex-row sm:flex-wrap sm:mt-0 sm:space-x-6");
			attr(div3, "class", "flex-1 min-w-0");
			attr(span0, "class", "hidden sm:block");
			attr(span1, "class", "hidden sm:block ml-3");
			attr(button2, "type", "button");
			attr(button2, "class", "inline-flex items-center px-4 py-2 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500");
			attr(span2, "class", "sm:ml-3");
			attr(span3, "class", "ml-3 relative sm:hidden");
			attr(div4, "class", "mt-5 flex lg:mt-0 lg:ml-4");
			attr(div5, "class", "lg:flex lg:items-center lg:justify-between");
			attr(span4, "class", "sm:ml-3");
			attr(div6, "class", "flex mb-4");
			attr(pre, "class", "whitespace-pre-wrap");
			attr(div7, "class", "px-4 py-6 sm:px-0");
			attr(div8, "class", "max-w-7xl mx-auto py-6 sm:px-6 lg:px-8");
		},
		m(target, anchor) {
			insert(target, div5, anchor);
			append(div5, div3);
			append(div3, h2);
			append(h2, t0);
			append(div3, t1);
			append(div3, div2);
			append(div2, div0);
			append(div0, svg0);
			append(svg0, path0);
			append(div0, t2);
			append(div0, t3);
			append(div2, t4);
			append(div2, div1);
			append(div1, svg1);
			append(svg1, path1);
			append(div1, t5);
			append(div1, t6);
			append(div5, t7);
			append(div5, div4);
			append(div4, span0);
			append(div4, t9);
			append(div4, span1);
			append(div4, t11);
			append(div4, span2);
			append(span2, button2);
			append(div4, t13);
			append(div4, span3);
			insert(target, t15, anchor);
			insert(target, div8, anchor);
			append(div8, div7);
			append(div7, div6);
			append(div6, span4);
			if (if_block) if_block.m(span4, null);
			append(div7, t16);
			append(div7, pre);
			append(pre, t17);

			if (!mounted) {
				dispose = listen(button2, "click", /*runDag*/ ctx[4]);
				mounted = true;
			}
		},
		p(ctx, dirty) {
			if (dirty & /*$dag_id*/ 2) set_data(t0, /*$dag_id*/ ctx[1]);
			if (dirty & /*$dag*/ 4 && t3_value !== (t3_value = /*$dag*/ ctx[2].schedule + "")) set_data(t3, t3_value);
			if (dirty & /*$dag*/ 4 && t6_value !== (t6_value = /*$dag*/ ctx[2].image + "")) set_data(t6, t6_value);
			if (/*pod*/ ctx[3]) if_block.p(ctx, dirty);
			if (dirty & /*logs*/ 1) set_data(t17, /*logs*/ ctx[0]);
		},
		d(detaching) {
			if (detaching) detach(div5);
			if (detaching) detach(t15);
			if (detaching) detach(div8);
			if (if_block) if_block.d();
			mounted = false;
			dispose();
		}
	};
}

// (101:10) {#if pod}
function create_if_block_1(ctx) {
	let t0;
	let span;

	return {
		c() {
			t0 = text("Running on pod ");
			span = element("span");
			span.textContent = `${/*pod*/ ctx[3]}`;
			attr(span, "class", "p-1 rounded bg-blue-200");
		},
		m(target, anchor) {
			insert(target, t0, anchor);
			insert(target, span, anchor);
		},
		p: noop,
		d(detaching) {
			if (detaching) detach(t0);
			if (detaching) detach(span);
		}
	};
}

function create_fragment(ctx) {
	let if_block_anchor;

	function select_block_type(ctx, dirty) {
		if (/*$dag*/ ctx[2]) return create_if_block;
		return create_else_block;
	}

	let current_block_type = select_block_type(ctx, -1);
	let if_block = current_block_type(ctx);

	return {
		c() {
			if_block.c();
			if_block_anchor = empty();
		},
		m(target, anchor) {
			if_block.m(target, anchor);
			insert(target, if_block_anchor, anchor);
		},
		p(ctx, [dirty]) {
			if (current_block_type === (current_block_type = select_block_type(ctx, dirty)) && if_block) {
				if_block.p(ctx, dirty);
			} else {
				if_block.d(1);
				if_block = current_block_type(ctx);

				if (if_block) {
					if_block.c();
					if_block.m(if_block_anchor.parentNode, if_block_anchor);
				}
			}
		},
		i: noop,
		o: noop,
		d(detaching) {
			if_block.d(detaching);
			if (detaching) detach(if_block_anchor);
		}
	};
}

function instance($$self, $$props, $$invalidate) {
	let $dag_id;
	let $dag;
	component_subscribe($$self, dag_id, $$value => $$invalidate(1, $dag_id = $$value));
	component_subscribe($$self, dag, $$value => $$invalidate(2, $dag = $$value));
	let { router } = $$props;
	let pod;
	let logs = "";
	let uint8array = new TextDecoder("utf-8");

	const runDag = async () => {
		// todo have some sort of ui state that shows its running
		const res = await fetch(`/run/${$dag_id}`, { method: "POST" });

		// to get to a POC just storing the current pod run after a triggered run
		// no history yet
		showLogs();
	};

	const showLogs = async () => {
		$$invalidate(0, logs = "");
	}; // const response = await fetch(`/api/logs/${pod}`)
	// const reader = response.body.getReader()
	// while (true){
	//   const { value, done } = await reader.read();

	$$self.$$set = $$props => {
		if ("router" in $$props) $$invalidate(5, router = $$props.router);
	};

	return [logs, $dag_id, $dag, pod, runDag, router];
}

class ViewDag extends SvelteComponent {
	constructor(options) {
		super();
		init(this, options, instance, create_fragment, safe_not_equal, { router: 5 });
	}
}

export default ViewDag;