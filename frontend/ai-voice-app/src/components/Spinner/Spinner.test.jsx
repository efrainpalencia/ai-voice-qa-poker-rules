import React from 'react';
import { shallow } from 'enzyme';
import Spinner from './Spinner';

describe('<Spinner />', () => {
  let component;

  beforeEach(() => {
    component = shallow(<Spinner />);
  });

  test('It should mount', () => {
    expect(component.length).toBe(1);
  });
});
