// Copyright 2016 Google Inc. All Rights Reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

package grumpy

import (
	"reflect"
)

// Traceback represents Python 'traceback' objects.
type Traceback struct {
	Object
	frame  *Frame     `attr:"tb_frame"`
	next   *Traceback `attr:"tb_next"`
	lineno int        `attr:"tb_lineno"`
}

func newTraceback(f *Frame, next *Traceback) *Traceback {
	f.taken = true
	t := &Traceback{Object{typ: TracebackType}, f, next, f.lineno}
	t.self = t
	return t
}

func toTracebackUnsafe(o *Object) *Traceback {
	return (*Traceback)(o.toPointer())
}

// ToObject upcasts f to an Object.
func (f *Traceback) ToObject() *Object {
	return &f.Object
}

// TracebackType is the object representing the Python 'traceback' type.
var TracebackType = newBasisType("traceback", reflect.TypeOf(Traceback{}), toTracebackUnsafe, ObjectType)

func initTracebackType(map[string]*Object) {
	TracebackType.flags &^= typeFlagInstantiable | typeFlagBasetype
}
